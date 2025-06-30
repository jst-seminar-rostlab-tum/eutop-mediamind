import asyncio
import base64
import json
import os
import re
import time

import tiktoken
from bs4 import BeautifulSoup, Comment
from openai import OpenAI
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.core.logger import get_logger
from app.services.web_harvester.utils import (
    change_frame,
    click_element,
    insert_credential,
    scroll_to_element,
)

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
    "4. 'refuse_notifications' - Xpath of the refuse notifications element\n"
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
    def _add_new_keys_to_newspaper(new_keys, newspaper):
        if new_keys:
            for key, value in new_keys.items():
                if value is not None and key not in ["name", "link"]:
                    if key in newspaper:
                        if isinstance(newspaper[key], list):
                            newspaper[key].append(value)
                        else:
                            existing_value = newspaper[key]
                            newspaper[key] = [existing_value, value]
                    else:
                        newspaper[key] = value

            logger.info("Successfully added new keys.")
            return newspaper
        else:
            logger.error("Failed to add new keys.")
            return None

    @staticmethod
    def _find_correct_clickable_element(driver, wait, newspaper, key):
        selectors = newspaper.get(key)
        if selectors:
            if isinstance(selectors, list):
                for xpath in selectors:
                    scroll_to_element(driver, wait, xpath, key)
                    if click_element(driver, wait, xpath, key):
                        newspaper[key] = xpath
                        return True
            else:
                scroll_to_element(driver, wait, selectors, key)
                if click_element(driver, wait, selectors, key):
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
                        logger.error(
                            f"Element {css_selector} not found in shadow root "
                            f"{shadow_xpath}"
                        )
            except Exception:
                logger.debug(
                    f"Error locating shadow host element {shadow_xpath}"
                )

        logger.error("No clickable element found inside shadow roots")
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
                        driver, wait, xpath, key, credential
                    ):
                        newspaper[key] = xpath
                        return True
            else:
                if click_element(
                    driver, wait, selectors, key
                ) and insert_credential(
                    driver, wait, selectors, key, credential
                ):
                    return True
        return False

    @staticmethod
    async def _call_LLM(
        LLM_model: str,
        html: str,
        instructions: str,
        response_schema: str,
        image_url: str,
    ):
        def sync_call():
            messages = [
                {
                    "role": "developer",
                    "content": f"{instructions}.\n{response_schema}",
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": html},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url,
                            },
                        },
                    ],
                },
            ]

            try:
                client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                completion = client.chat.completions.create(
                    model=LLM_model, messages=messages, temperature=0.1
                )
                return completion.choices[0].message.content
            except Exception as e:
                logger.error(f"Error at calling OpenAI API: {e}")
                return None

        return await asyncio.to_thread(sync_call)

    @staticmethod
    async def _extract_and_merge_dynamic_content(driver, html):
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

        # Insert shadow roots content in original html
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

        return str(target)

    @staticmethod
    def _count_tokens(text, LLM_model):
        enc = tiktoken.encoding_for_model(LLM_model)
        return len(enc.encode(text))

    async def _find_elements_with_LLM(
        driver, instructions, response_schema, newspaper, LLM_model
    ):
        html = driver.page_source
        html = await LoginLLM._extract_and_merge_dynamic_content(driver, html)
        html = LoginLLM._custom_clean_html(html)
        with open("html.txt", "w", encoding="utf-8") as file:
            file.write(html)
        logger.info(
            f"Tokens in HTML: {LoginLLM._count_tokens(html, LLM_model)}"
        )
        time.sleep(3)
        website_image = LoginLLM._take_screenshot(driver)
        LLM_result_raw = await LoginLLM._call_LLM(
            LLM_model, html, instructions, response_schema, website_image
        )
        LLM_result = LoginLLM._llm_response_to_json(LLM_result_raw)
        updated_newspaper = LoginLLM._add_new_keys_to_newspaper(
            LLM_result, newspaper
        )
        return updated_newspaper

    @staticmethod
    async def _execute_attempt_login(
        driver, wait, newspaper, LLM_model, username, password
    ):
        instructions = instructions_login
        response_schema = login_schema
        updated_neswspaper = await LoginLLM._find_elements_with_LLM(
            driver, instructions, response_schema, newspaper, LLM_model
        )
        logged_in = False

        # Accept cookies in shadow root
        cookies_accepted = False
        if updated_neswspaper.get("shadow_host_cookies"):
            cookies_accepted = LoginLLM._click_shadow_root_element(
                driver,
                wait,
                updated_neswspaper,
                "shadow_host_cookies",
                "cookies_button",
            )

        # Accept cookies
        if not cookies_accepted:
            # Change to cookies iframe
            LoginLLM._change_to_correct_iframe(
                driver, wait, updated_neswspaper, "iframe_cookies"
            )
            # Click cookies button
            LoginLLM._find_correct_clickable_element(
                driver, wait, updated_neswspaper, "cookies_button"
            )
        driver.switch_to.default_content()

        # Remove notifications window
        LoginLLM._find_correct_clickable_element(
            driver, wait, updated_neswspaper, "refuse_notifications"
        )

        # Go to section containing login element
        LoginLLM._find_correct_clickable_element(
            driver, wait, updated_neswspaper, "path_to_login_button"
        )

        # Open login form
        LoginLLM._find_correct_clickable_element(
            driver, wait, updated_neswspaper, "login_button"
        )

        # We check if the login form is in this scraped page
        if updated_neswspaper.get("submit_button"):
            # Change to credentials iframe
            LoginLLM._change_to_correct_iframe(
                driver, wait, updated_neswspaper, "iframe_credentials"
            )
            # Insert credentials
            user_inserted = LoginLLM._find_correct_input_element(
                driver, wait, updated_neswspaper, "user_input", username
            )
            password_inserted = LoginLLM._find_correct_input_element(
                driver, wait, updated_neswspaper, "password_input", password
            )
            # Submit credentials
            submitted = LoginLLM._find_correct_clickable_element(
                driver, wait, updated_neswspaper, "submit_button"
            )
            driver.switch_to.default_content()

        if user_inserted and password_inserted and submitted:
            logged_in = True

        return logged_in

    @staticmethod
    async def add_page(name, url, username, password, LLM_model):
        # Obtain file with current registered newspapers
        try:
            with open("app/services/newspapers_data.json", "r") as file:
                newspapers = json.load(file)
        except FileNotFoundError:
            logger.error("Newspapers data .json not found")
            return None

        # Create the new newspaper JSON object
        new_key = f"newspaper{len(newspapers['newspapers'])+1}"
        newspapers["newspapers"][new_key] = {"name": name, "link": url}
        new_newspaper = newspapers["newspapers"][new_key]

        # Initialize Selenium
        chrome_options = Options()
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_extension("./cookie-blocker.crx")
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 5)
        driver.get(url)
        driver.maximize_window()
        time.sleep(3)

        # Variables to control login flow
        max_attempts = 8
        attempt = 0
        logged_in = False

        logger.info(f"Initializing LLM login process for newspaper: {name}")
        while attempt < max_attempts and not logged_in:
            attempt += 1
            logger.info(f"Login attempt {attempt}/{max_attempts}")
            try:
                logged_in = await LoginLLM._execute_attempt_login(
                    driver, wait, new_newspaper, LLM_model, username, password
                )
                if logged_in:
                    logger.info(f"Login completed at attempt {attempt}")
            except Exception:
                logger.info(
                    f"Login couldn't be completed at attempt {attempt}"
                )
                continue

        # Save the new newspaper in the JSON
        if logged_in:
            try:
                with open(
                    "app/services/updated_newspapers_data.json",
                    "w",
                    encoding="utf-8",
                ) as file:
                    json.dump(newspapers, file, indent=4, ensure_ascii=False)
                logger.info(
                    f"Login elements from newspaper {name} successfully added"
                )
            except Exception:
                logger.error(f"Error at adding newspaper {name}")
        else:
            logger.error(f"Login was not possible on newspaper {name}")

        time.sleep(300)

        driver.quit()
