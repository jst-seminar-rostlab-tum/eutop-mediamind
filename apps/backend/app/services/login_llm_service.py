import asyncio
import base64
import json
import math
import re
import time
from asyncio import Semaphore

import tiktoken
from bs4 import BeautifulSoup, Comment
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.core.db import async_session
from app.core.logger import get_logger
from app.models.subscription import Subscription
from app.repositories.subscription_repository import SubscriptionRepository
from app.services.llm_service.llm_client import LLMClient, LLMModels
from app.services.web_harvester.utils.web_utils import (
    change_frame,
    click_element,
    get_account_credentials,
    insert_credential,
    scroll_to_element,
)

MAX_TOKENS = 100000
MAX_CONCURRENCY = 10

logger = get_logger(__name__)

# Instructions to search for elements in the html
instructions_login = (
    "Analyze the website's html and extract login elements. "
    "For each element, provide the selector that would work with Selenium. "
    "Take into consideration that in this html the content of a Shadow DOM is "
    "inside of a '<div data-shadow-host='ID'> </div>' tag, in which the ID "
    "references the ID of the shadow host. "
    "Retrieve these elements if they exist in the html:\n"
    "1. 'shadow_host_cookies' - CSS Selector of the shadow host that contains "
    "the shadow DOM content with the accept cookies element (use the id for "
    "the CSS Selector)\n"
    "2. 'iframe_cookies' - Xpath of the iframe that contains the accept "
    "cookies element\n"
    "3. 'cookies_button' - Xpath of the accept cookies element itself "
    "(provide CSS Selector instead of Xpath only if this element is inside "
    "a shadow DOM)\n"
    "4. 'refuse_notifications' - Xpath to refuse notifications or remove ads\n"
    "5. 'path_to_login_button' - Xpath of the element that triggers the "
    "login element (for example, xpath of dropdown menu containing login "
    "button/link)\n"
    "6. 'login_button' - Xpath of login element itself\n"
    "7. 'iframe_credentials' — XPath of the iframe *that contains the "
    "credential input fields*, if any.\n"
    "8. 'user_input' — XPath of the input field where the username or "
    "email is typed.\n"
    "9. 'password_input' — XPath of the input field for the password.\n"
    "10. 'submit_button' — XPath of the element (usually a button) that "
    "submits the login form.\n"
    "Only include elements that actually exist on the page. "
    "The selectors must be robust and preferably use attributes like 'id', "
    "'name', or 'data-testid'. "
    "If you use text content, classes or other attributes, make them robust "
    "(for example, include many classes). "
    "A screenshot of the website is provided, use it to better identify "
    "the elements. "
)

# Instructions of the schema the response should be in
login_schema = """
Return the output as a valid JSON object, do not include any explanations,
Markdown formatting, or text before or after the JSON.
Use the following schema:\n
{
  "shadow_host_cookies": null,
  "iframe_cookies": null,
  "cookies_button": null,
  "refuse_notifications": null,
  "path_to_login_button": null,
  "login_button": null,
  "iframe_credentials": null,
  "user_input": null,
  "password_input": null,
  "submit_button": null
}
"""


class LoginLLM:
    cookies_accepted = False
    notifications_removed = False
    user_inserted = False
    password_inserted = False
    submitted = False
    semaphore = Semaphore(MAX_CONCURRENCY)

    @staticmethod
    def _reset_flags():
        LoginLLM.cookies_accepted = False
        LoginLLM.notifications_removed = False
        LoginLLM.user_inserted = False
        LoginLLM.password_inserted = False
        LoginLLM.submitted = False

    @staticmethod
    def _take_screenshot(driver):
        try:
            screenshot_bytes = driver.get_screenshot_as_png()
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode(
                "utf-8"
            )
            image_url = f"data:image/png;base64,{screenshot_base64}"
            logger.info("Screenshot successfully taken")
            return image_url
        except Exception:
            logger.error("Error at taking the screenshot")

    @staticmethod
    def _wait_for_page_change(driver):
        time.sleep(5)
        try:
            logs = driver.get_log("performance")
            for entry in logs:
                message = entry["message"]
                if (
                    '"Network.responseReceived"' in message
                    and '"status":200' in message
                ):
                    logger.info("200 OK response after submitting credentials")
                    return True
            logger.info("No 200 OK response, still not logged in")
        except Exception:
            logger.error("Error at accessing network logs")
            return False

    @staticmethod
    def _llm_response_to_json(raw_response: str) -> str:
        try:
            cleaned_response = re.sub(
                r"^```(?:json)?\s*|\s*```$", "", raw_response.strip()
            )
            json_reponse = json.loads(cleaned_response)
            return json_reponse
        except json.JSONDecodeError:
            logger.error("Error parsing LLM JSON response")
            return None

    @staticmethod
    def _add_new_keys_to_config(new_keys, config):
        if new_keys:
            for key, value in new_keys.items():
                if value is not None:
                    if key in config:
                        if isinstance(config[key], list):
                            config[key].append(value)
                        else:
                            existing_value = config[key]
                            config[key] = [existing_value, value]
                    else:
                        config[key] = value
            logger.info("Successfully added new keys.")
            return config
        else:
            logger.warning("Failed to add new keys.")
            return None

    @staticmethod
    def _find_correct_clickable_element(
        driver, wait, newspaper, key, second_button=None
    ):
        selectors = newspaper.get(key)
        if selectors:
            if isinstance(selectors, list):
                for xpath in selectors:
                    scroll_to_element(driver, wait, xpath, key)
                    if click_element(driver, wait, xpath, key):
                        if second_button:
                            newspaper[second_button] = xpath
                        else:
                            newspaper[key] = xpath
                        return True
            else:
                scroll_to_element(driver, wait, selectors, key)
                if click_element(driver, wait, selectors, key):
                    if second_button:
                        newspaper[second_button] = selectors
                    return True
        return False

    @staticmethod
    def _change_to_correct_iframe(driver, wait, newspaper, key):
        selectors = newspaper.get(key)
        if selectors:
            if isinstance(selectors, list):
                for xpath in selectors:
                    if change_frame(driver, wait, xpath, key):
                        newspaper[key] = xpath
                        break
            else:
                change_frame(driver, wait, selectors, key)

    @staticmethod
    def _find_correct_input_element(driver, wait, newspaper, key, credential):
        selectors = newspaper.get(key)
        if selectors:
            if isinstance(selectors, list):
                for xpath in selectors:
                    if click_element(
                        driver, wait, xpath, key
                    ) and insert_credential(
                        driver,
                        wait,
                        credential,
                        xpath,
                        key,
                    ):
                        newspaper[key] = xpath
                        return True
            else:
                if click_element(
                    driver, wait, selectors, key
                ) and insert_credential(
                    driver, wait, credential, selectors, key
                ):
                    return True
        return False

    @staticmethod
    def _click_shadow_root_element(
        driver, wait, newspaper, key_shadow, key_cookies
    ):
        shadow_selectors = newspaper.get(key_shadow)
        cookies_selectors = newspaper.get(key_cookies)

        if not shadow_selectors or not cookies_selectors:
            logger.warning("Shadow selectors or cookies selectors missing")
            return False

        if not isinstance(shadow_selectors, list):
            shadow_selectors = [shadow_selectors]
        if not isinstance(cookies_selectors, list):
            cookies_selectors = [cookies_selectors]

        for shadow_xpath in shadow_selectors:
            try:
                shadow_host = wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, shadow_xpath)
                    )
                )
                shadow_root = driver.execute_script(
                    "return arguments[0].shadowRoot", shadow_host
                )
                if not shadow_root:
                    logger.warning(
                        f"No shadow root found for host {shadow_xpath}"
                    )
                    continue

                for css_selector in cookies_selectors:
                    try:
                        clickable_element = shadow_root.find_element(
                            By.CSS_SELECTOR, css_selector
                        )
                        try:
                            clickable_element.click()
                            logger.info(
                                f"Clicked element {css_selector} "
                                f"inside shadow "
                                f"root {shadow_xpath}"
                            )
                            newspaper[key_shadow] = shadow_xpath
                            newspaper[key_cookies] = css_selector
                            return True
                        except Exception:
                            try:
                                driver.execute_script(
                                    "arguments[0].click();", clickable_element
                                )
                                newspaper[key_shadow] = shadow_xpath
                                newspaper[key_cookies] = css_selector
                                logger.info(
                                    f"Clicked element {css_selector} inside "
                                    f"shadow root {shadow_xpath}"
                                )
                                return True
                            except Exception:
                                logger.debug(
                                    f"Could not click element {css_selector} "
                                    f"inside shadow root {shadow_xpath}"
                                )
                    except Exception:
                        logger.warning(
                            f"Element {css_selector} not found in shadow root "
                            f"{shadow_xpath}"
                        )
            except Exception:
                logger.debug(
                    f"Error locating shadow host element {shadow_xpath}"
                )

        logger.warning("No clickable element found inside shadow roots")
        return False

    @staticmethod
    def _custom_clean_html(raw_html):
        soup = BeautifulSoup(raw_html, "html.parser")

        body = soup.find("body")

        if body:
            target = body
        else:
            target = soup

        for tag in target(["script", "style", "noscript"]):
            tag.decompose()

        for comment in target.find_all(
            string=lambda text: isinstance(text, Comment)
        ):
            comment.decompose()
        # Eliminate SVG instructions
        for path_tag in target.find_all("path"):
            if "d" in path_tag.attrs:
                del path_tag.attrs["d"]

        return str(target)

    @staticmethod
    async def _extract_and_merge_shadow_roots(driver, html):
        # Extract shadow roots content
        shadow_contents = {}
        shadow_hosts = driver.execute_script(
            """
            return Array.from(document.querySelectorAll('*'))
                .filter(el => el.shadowRoot)
                .map(el => {
                    return {
                        id: el.id || null,
                        tag: el.tagName,
                        classes: el.className || null,
                        shadowHtml: el.shadowRoot.innerHTML
                    };
                });
        """
        )
        for host in shadow_hosts:
            identifier = host["id"]
            shadow_contents[identifier] = host["shadowHtml"]

        # Insert shadow roots content in original html
        soup_final = BeautifulSoup(html, "html.parser")
        for element in soup_final.find_all(True):
            if element.get("id") and element.get("id") in shadow_contents:
                shadow_html = shadow_contents[element.get("id")]
                shadow_root_tag = soup_final.new_tag("div")
                shadow_root_tag["data-shadow-host"] = element.get("id")
                shadow_inner_soup = BeautifulSoup(shadow_html, "html.parser")
                for child in shadow_inner_soup.find_all(recursive=False):
                    shadow_root_tag.append(child)
                element.append(shadow_root_tag)

        return soup_final.prettify()

    @staticmethod
    async def _extract_and_merge_iframes(driver, html):
        soup = BeautifulSoup(html, "html.parser")

        # Extract the content of each iframe
        iframe_contents = {}
        for i, iframe in enumerate(soup.find_all("iframe")):
            iframe_id = iframe.get("id")
            if iframe_id:
                try:
                    driver.switch_to.frame(iframe_id)
                    iframe_html = driver.page_source
                    iframe_contents[iframe_id] = iframe_html
                    driver.switch_to.default_content()
                except Exception as e:
                    logger.warning(f"Error accessing iframe {iframe_id}: {e}")
                    driver.switch_to.default_content()

        # Insert iframe content in original html
        soup_final = BeautifulSoup(html, "html.parser")
        for iframe in soup_final.find_all("iframe"):
            iframe_id = iframe.get("id")
            if iframe_id and iframe_id in iframe_contents:
                extracted_html = BeautifulSoup(
                    iframe_contents[iframe_id], "html.parser"
                )
                inner_content = extracted_html.find().decode_contents()
                iframe.append(BeautifulSoup(inner_content, "html.parser"))

        return soup_final.prettify()

    @staticmethod
    def _count_tokens(text):
        enc = tiktoken.encoding_for_model(LLMModels.openai_4o.value)
        return len(enc.encode(text))

    @staticmethod
    async def _send_chunk_to_llm(
        client, html_chunk, website_image, login_config
    ):
        try:
            async with LoginLLM.semaphore:
                prompt = (
                    f"{instructions_login}\n\n{login_schema}\n\n"
                    f"Avoid the following existing values: "
                    f"\n{login_config}\n"
                    f"These values have been tested already and do not "
                    f"work, return new and different ones.\n\n"
                    f"\nHTML Content:\n{html_chunk}\n"
                )
                return await asyncio.to_thread(
                    client.generate_response, prompt, 0.1, website_image
                )
        except Exception as e:
            logger.warning(f"LLM call failed for chunk: {e}")
            return None

    @staticmethod
    def _split_html(html: str, max_tokens: int) -> list[str]:
        tokens = LoginLLM._count_tokens(html)
        if tokens <= max_tokens:
            return [html]

        chunk_size = len(html) // math.ceil(tokens / max_tokens)
        chunks = [
            html[i : i + chunk_size] for i in range(0, len(html), chunk_size)
        ]
        logger.info(f"Split HTML into {len(chunks)} chunks")
        return chunks

    @staticmethod
    async def _find_elements_with_LLM(driver, login_config):
        html = driver.page_source
        html = await LoginLLM._extract_and_merge_iframes(driver, html)
        html = await LoginLLM._extract_and_merge_shadow_roots(driver, html)
        html = LoginLLM._custom_clean_html(html)
        tokens = LoginLLM._count_tokens(html)
        logger.info(f"Html tokens to be sent to the LLM: {tokens}")
        await asyncio.sleep(3)
        website_image = LoginLLM._take_screenshot(driver)
        try:
            client = LLMClient(LLMModels.openai_4o)
            html_chunks = LoginLLM._split_html(html, MAX_TOKENS)
            tasks = [
                LoginLLM._send_chunk_to_llm(
                    client, chunk, website_image, login_config
                )
                for chunk in html_chunks
            ]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            updated_config = login_config
            for resp in responses:
                if isinstance(resp, Exception):
                    logger.error(f"Concurrent call failed: {resp}")
                    continue
                LLM_result = LoginLLM._llm_response_to_json(resp)
                if LLM_result is None:
                    logger.warning("Skipping response due to JSON parse error.")
                    continue
                updated_config = LoginLLM._add_new_keys_to_config(
                    LLM_result, updated_config
                )
            return updated_config
        except Exception as e:
            logger.error(f"Error while calling LLMClient: {e}")
            return

    @staticmethod
    async def _execute_login_attempt(
        driver, wait, login_config, username, password
    ):
        updated_config = await LoginLLM._find_elements_with_LLM(
            driver,
            login_config,
        )

        logged_in = False
        if not LoginLLM.user_inserted:
            LoginLLM.password_inserted = False

        # Accept cookies in shadow root
        if (
            updated_config.get("shadow_host_cookies")
            and not LoginLLM.cookies_accepted
        ):
            LoginLLM.cookies_accepted = LoginLLM._click_shadow_root_element(
                driver,
                wait,
                updated_config,
                "shadow_host_cookies",
                "cookies_button",
            )

        # Accept cookies
        if not LoginLLM.cookies_accepted:
            # Change to cookies iframe
            LoginLLM._change_to_correct_iframe(
                driver, wait, updated_config, "iframe_cookies"
            )
            # Click cookies button
            LoginLLM.cookies_accepted = (
                LoginLLM._find_correct_clickable_element(
                    driver, wait, updated_config, "cookies_button"
                )
            )
        driver.switch_to.default_content()

        # Remove notifications window
        if not LoginLLM.notifications_removed:
            LoginLLM.notifications_removed = (
                LoginLLM._find_correct_clickable_element(
                    driver, wait, updated_config, "refuse_notifications"
                )
            )

        # Go to section containing login section trigger
        LoginLLM._find_correct_clickable_element(
            driver, wait, updated_config, "path_to_login_button"
        )

        # Open login form
        LoginLLM._find_correct_clickable_element(
            driver, wait, updated_config, "login_button"
        )

        # Change to credentials iframe
        LoginLLM._change_to_correct_iframe(
            driver, wait, updated_config, "iframe_credentials"
        )

        # Insert and submit credentials
        if LoginLLM.user_inserted and LoginLLM.submitted:
            LoginLLM.password_inserted = LoginLLM._find_correct_input_element(
                driver, wait, updated_config, "password_input", password
            )
            # Clean the network logs
            _ = driver.get_log("performance")
            # Submit credentials
            LoginLLM.submitted = LoginLLM._find_correct_clickable_element(
                driver,
                wait,
                updated_config,
                "submit_button",
                second_button="second_submit_button",
            )
            driver.switch_to.default_content()
        else:
            # Insert credentials
            if not LoginLLM.user_inserted:
                LoginLLM.user_inserted = LoginLLM._find_correct_input_element(
                    driver, wait, updated_config, "user_input", username
                )
            if not LoginLLM.password_inserted:
                LoginLLM.password_inserted = (
                    LoginLLM._find_correct_input_element(
                        driver,
                        wait,
                        updated_config,
                        "password_input",
                        password,
                    )
                )
            # Clean the network logs
            _ = driver.get_log("performance")
            # Submit credentials
            LoginLLM.submitted = LoginLLM._find_correct_clickable_element(
                driver, wait, updated_config, "submit_button"
            )
            driver.switch_to.default_content()

        if (
            LoginLLM.user_inserted
            and LoginLLM.password_inserted
            and LoginLLM.submitted
        ):
            page_changed = LoginLLM._wait_for_page_change(driver)
            if page_changed:
                logged_in = True
        return logged_in

    @staticmethod
    async def add_page(subscription: Subscription):
        credentials = get_account_credentials(subscription)
        if credentials is None:
            logger.error(
                f"No credentials found for subscription: {subscription.name}."
            )
            return False
        else:
            username, password = credentials

        # Initialize Selenium
        chrome_options = Options()
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.set_capability(
            "goog:loggingPrefs", {"performance": "ALL"}
        )
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 5)
        driver.get(subscription.domain)
        time.sleep(3)

        # Variables to control login flow
        max_attempts = 8
        attempt = 0
        logged_in = False
        login_config = {}

        logger.info(
            f"Initializing LLM login process for "
            f"newspaper: {subscription.name}"
        )
        while attempt < max_attempts and not logged_in:
            attempt += 1
            logger.info(f"Login attempt {attempt}/{max_attempts}")
            try:
                logged_in = await LoginLLM._execute_login_attempt(
                    driver, wait, login_config, username, password
                )
                if logged_in:
                    logger.info(f"Login completed at attempt {attempt}")
            except Exception:
                logger.info(
                    f"Login couldn't be completed at attempt {attempt}"
                )
                continue

        driver.quit()

        LoginLLM._reset_flags()

        if logged_in:
            async with async_session() as session:
                db_subscription = await SubscriptionRepository.get_by_id(
                    session, subscription.id
                )
                db_subscription.login_config = login_config
                await SubscriptionRepository.update(session, db_subscription)
                logger.info(f"Login config updated for {db_subscription.name}")
                return db_subscription
        else:
            logger.warning(
                f"Login was not possible on newspaper {subscription.name}"
            )
            return False
