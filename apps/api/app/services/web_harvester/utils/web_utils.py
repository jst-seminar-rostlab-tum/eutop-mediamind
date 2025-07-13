import json
import logging
import time
import urllib.request

from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import webdriver

from app.core.config import configs
from app.core.logger import get_logger
from app.models.subscription import Subscription

logger = get_logger(__name__)

# Suppress Selenium Wire INFO logs
logging.getLogger("seleniumwire").setLevel(logging.WARNING)


def check_proxy_availability(proxy_url: str) -> bool:
    """
    Check if the proxy URL is available.
    Returns True if the proxy is available, False otherwise.
    """
    url = "http://httpbin.org/ip"

    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({"https": proxy_url, "http": proxy_url})
    )

    try:
        opener.open(url, timeout=10)
        return True
    except Exception as e:
        logger.warning(
            f"Proxy {proxy_url} is not available: {e}"
            "Using direct connection instead."
        )
        return False


def create_driver(headless: bool = True, use_proxy: bool = False):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument(
        "--enable-features=NetworkService,NetworkServiceInProcess"
    )
    chrome_options.add_argument("--disable-gpu")
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    chrome_options.add_argument(f"--user-agent={UserAgent().random}")

    # Configure selenium-wire options for proxy
    seleniumwire_options = {}
    if use_proxy and check_proxy_availability(configs.PROXY_URL):
        seleniumwire_options = {
            "proxy": {
                "http": configs.PROXY_URL,
                "https": configs.PROXY_URL,
                "no_proxy": "localhost,127.0.0.1",
            },
            "connection_timeout": 15,
            "read_timeout": 15,
        }

    driver = webdriver.Chrome(
        options=chrome_options, seleniumwire_options=seleniumwire_options
    )
    driver.set_window_size(1920, 1080)
    driver.set_page_load_timeout(10)  # Set a timeout for page loading
    driver.command_executor.set_timeout(50)

    wait = WebDriverWait(driver, 5)

    return driver, wait


def click_element(driver, wait, selector_xpath, selector_name):
    try:
        time.sleep(1)
        if selector_xpath.startswith("class="):
            btn = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.CLASS_NAME,
                        selector_xpath.replace("class=", "").split()[0],
                    )
                )
            )
        elif selector_xpath.startswith("//"):
            btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, selector_xpath))
            )
        else:
            btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector_xpath))
            )
        try:
            btn.click()
            logger.info(f"Element {selector_name} clicked")
            return True
        except Exception:
            try:
                driver.execute_script("arguments[0].click();", btn)
                logger.info(f"Element {selector_name} clicked")
                return True
            except Exception:
                logger.error(
                    f"Was not possible to click element {selector_name}"
                )
                return False
    except Exception:
        logger.error(f"Element to click {selector_name} not found")
        return False


def click_shadow_element(
    driver, wait, element_selector, shadow_selector, element_name, shadow_name
):
    try:
        time.sleep(1)
        shadow_host = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, shadow_selector))
        )
        shadow_root = driver.execute_script(
            "return arguments[0].shadowRoot", shadow_host
        )
        clickable_element = shadow_root.find_element(
            By.CSS_SELECTOR, element_selector
        )
        try:
            clickable_element.click()
            logger.info(
                f"Button {element_name} clicked in shadow root {shadow_name}"
            )
            return True
        except Exception:
            try:
                driver.execute_script(
                    "arguments[0].click();", clickable_element
                )
                logger.info(
                    f"Button {element_name} clicked "
                    f"in shadow root {shadow_name}"
                )
                return True
            except Exception:
                logger.error(
                    f"Was not possible to click element {element_name} "
                    f"in {shadow_name}"
                )
                return False
    except Exception:
        logger.error(
            f"Element {element_name} in shadow root {shadow_name} not found"
        )
        return False


def change_frame(driver, wait, selector_xpath, selector_name):
    try:
        iframe = wait.until(
            EC.presence_of_element_located((By.XPATH, selector_xpath))
        )
        driver.switch_to.frame(iframe)
        logger.info(f"Changed to iframe: {selector_name}")
        return True
    except Exception:
        logger.error(f"Error when changing to iframe: {selector_name}")
        return False


def scroll_to_element(driver, wait, selector_xpath, selector_name):
    try:
        element = wait.until(
            EC.visibility_of_element_located((By.XPATH, selector_xpath))
        )
        driver.execute_script(
            "arguments[0].scrollIntoView({"
            "block: 'center', "
            "behavior: 'instant'"
            "});",
            element,
        )
        time.sleep(1)

        logger.info(f"Scrolled to element {selector_name}")
        return True
    except Exception:
        logger.error(f"Failed to scroll to element {selector_name}")
        return False


def insert_credential(driver, wait, credential, input_selector, input_name):
    try:
        if input_selector.startswith("//"):
            input_field = wait.until(
                EC.presence_of_element_located((By.XPATH, input_selector))
            )
        else:
            input_field = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, input_selector)
                )
            )
        input_field.clear()
        input_field.send_keys(credential)
        time.sleep(1)
        logger.info(f"Credential inserted for {input_name}")
        return True
    except Exception:
        logger.warning(f"Could not insert credential for {input_name}")
        return False


def get_account_credentials(subscription):
    username = subscription.username
    password = subscription.secrets
    if not username or not password:
        return None
    return username, password


def accept_cookies(driver, wait, paper):
    # Change to cookies iframe
    iframe_key = "iframe_cookies"
    if paper.get(iframe_key):
        change_frame(driver, wait, paper[iframe_key], iframe_key)

    # Accept cookies
    button_key = "cookies_button"
    shadow_dom_key = "shadow_host_cookies"
    if paper.get(shadow_dom_key) and paper.get(button_key):
        click_shadow_element(
            driver,
            wait,
            paper[button_key],
            paper[shadow_dom_key],
            button_key,
            shadow_dom_key,
        )
    elif paper.get(button_key):
        if not click_element(driver, wait, paper[button_key], button_key):
            try:
                logger.info("Searching for unregistered cookies iframe")
                iframe = driver.find_element(
                    By.CSS_SELECTOR, "iframe[id^='sp_message_iframe']"
                )
                logger.info("Unregistered cookies iframe found")
                driver.switch_to.frame(iframe)
                time.sleep(1)
                click_element(driver, wait, paper[button_key], button_key)
            except Exception:
                logger.warning("Was not possible to accept cookies")
    driver.switch_to.default_content()  # Always switch back to main context


def remove_notifications(driver, wait, paper):
    key = "refuse_notifications"
    if paper.get(key):
        click_element(driver, wait, paper[key], key)


def open_login_form(driver, wait, paper):
    path_key = "path_to_login_button"
    if paper.get(path_key):
        click_element(driver, wait, paper[path_key], path_key)
    button_key = "login_button"
    if paper.get(button_key):
        click_element(driver, wait, paper[button_key], button_key)


def submit_login_credentials(driver, wait, paper, username, password):
    iframe_key = "iframe_credentials"
    if paper.get(iframe_key):
        change_frame(driver, wait, paper[iframe_key], iframe_key)

    # Insert and submit credentials
    user_key = "user_input"
    password_key = "password_input"
    first_button_key = "submit_button"
    second_button_key = "second_submit_button"
    if paper.get(user_key):
        click_element(driver, wait, paper[user_key], user_key)
        insert_credential(driver, wait, username, paper[user_key], user_key)
    if paper.get(second_button_key) and paper.get(first_button_key):
        scroll_to_element(
            driver, wait, paper[first_button_key], first_button_key
        )
        click_element(driver, wait, paper[first_button_key], first_button_key)
    if paper.get(password_key):
        click_element(driver, wait, paper[password_key], password_key)
        insert_credential(
            driver, wait, password, paper[password_key], password_key
        )
    if paper.get(second_button_key):
        scroll_to_element(
            driver, wait, paper[second_button_key], second_button_key
        )
        if not click_element(
            driver, wait, paper[second_button_key], second_button_key
        ):
            logger.error("Failed to click second submit button")
            return False
        return True
    elif paper.get(first_button_key):
        scroll_to_element(
            driver, wait, paper[first_button_key], first_button_key
        )
        if not click_element(
            driver, wait, paper[first_button_key], first_button_key
        ):
            logger.error("Failed to click submit button")
            return False
        return True
    driver.switch_to.default_content()  # Always switch back to main context


def hardcoded_login(driver, wait, subscription: Subscription):
    # Load newspapers accounts
    credentials = get_account_credentials(subscription)
    if credentials is None:
        logger.error(
            f"No credentials found for subscription: {subscription.name}."
        )
        return False
    else:
        username, password = credentials

    config = subscription.login_config
    if not config:
        logger.error(
            f"No configuration found for newspaper: {subscription.name}"
        )
        return False

    # Initialize newspaper website
    try:
        driver.get(subscription.domain)
    except Exception:
        logger.error(f"No link provided for: {subscription.name}")
        return False

    logger.info(f"Processing login to: {subscription.name}")
    accept_cookies(driver, wait, config)
    remove_notifications(driver, wait, config)
    open_login_form(driver, wait, config)
    return submit_login_credentials(driver, wait, config, username, password)


def hardcoded_logout(driver, wait, subscription: Subscription):
    paper = subscription.login_config

    # Go to profile section
    profile_key = "profile_section"
    if paper.get(profile_key):
        click_element(driver, wait, paper[profile_key], profile_key)

    # Change to logout iframe
    iframe_key = "iframe_logout"
    if paper.get(iframe_key):
        change_frame(driver, wait, paper[iframe_key], iframe_key)

    # Logout
    logout_key = "logout_button"
    if paper.get(logout_key):
        if not click_element(driver, wait, paper[logout_key], logout_key):
            logger.error("Failed to logout from page")
            return False
        return True

    return False


def get_response_code(driver, url):
    """
    Get the HTTP response code of the main page after loading it in the
    browser. This function uses the performance logs to find the response
    code of the main page.
    """
    logs = driver.get_log("performance")
    main_page_status = 404

    for log in logs:
        message = json.loads(log["message"])
        if message["message"]["method"] == "Network.responseReceived":
            response = message["message"]["params"]["response"]
            response_url = response["url"]

            # Check if this is the main page (exact match or main document)
            if response_url == url or response["mimeType"] == "text/html":
                main_page_status = response["status"]
                break
    return main_page_status
