# import json
import logging
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def change_frame(driver, frame):
    try:
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, frame))
        )
        driver.switch_to.frame(iframe)
        logger.info("Changed to iframe")
    except Exception as e:
        logger.error(f"Error when changing frames: {e}")


def insert_credential(driver, credential, xpath_input_field):
    try:
        input_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath_input_field))
        )
        input_field.clear()
        input_field.send_keys(credential)
        time.sleep(1)

        logger.info("Credential inserted")
        return True
    except Exception as e:
        logger.warning(f"Could not insert credential: {e}")
        return False


def scroll_to_element(driver, element_xpath):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, element_xpath))
        )
        driver.execute_script(
            "arguments[0].scrollIntoView({"
            "block: 'center', "
            "behavior: 'instant'"
            "});",
            element,
        )
        time.sleep(1)

        logger.info("Scrolled to element")
        return True
    except Exception as e:
        logger.error(f"Failed to scroll to element: {e}")
        return False


def click_element(driver, element_xpath):
    try:
        time.sleep(1)
        clickable_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, element_xpath))
        )
        try:
            clickable_element.click()
            logger.info("Element clicked")
            return True
        except Exception:
            logger.info("Trying to click element with JavaScript")
            try:
                driver.execute_script(
                    "arguments[0].click();", clickable_element
                )
                logger.info("Element clicked")
                return True
            except Exception as e:
                logger.error(f"Was not possible to click element: {e}")
                return False
    except Exception as e:
        logger.error(f"Element to click not found: {e}")
        return False


def click_shadow_element(driver, element, shadow):
    try:
        time.sleep(1)
        shadow_host = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, shadow))
        )
        shadow_root = driver.execute_script(
            "return arguments[0].shadowRoot", shadow_host
        )
        clickable_element = shadow_root.find_element(By.CSS_SELECTOR, element)

        try:
            clickable_element.click()
            logger.info("Button clicked")
            return True
        except Exception:
            try:
                driver.execute_script(
                    "arguments[0].click();", clickable_element
                )
                logger.info("Button clicked with JavaScript")
                return True
            except Exception as e:
                logger.error(
                    f"Was not possible to click element in shadow DOM: {e}"
                )
                return False
    except Exception as e:
        logger.error(f"Element to click not found: {e}")
        return False


def login_paywalled_website(driver, username, password, site_data):
    # Change to cookies iframe
    if site_data.get("iframe_cookies"):
        change_frame(driver, site_data["iframe_cookies"])

    # Accept cookies
    if site_data.get("shadow_cookies") and site_data.get("cookies_button"):
        click_shadow_element(
            driver, site_data["cookies_button"], site_data["shadow_cookies"]
        )
    elif site_data.get("cookies_button"):
        click_element(driver, site_data["cookies_button"])
    driver.switch_to.default_content()

    # Remove notifications window
    if site_data.get("refuse_notifications"):
        click_element(driver, site_data["refuse_notifications"])

    # Go to login section
    if site_data.get("path_to_login_button"):
        click_element(driver, site_data["path_to_login_button"])
    if site_data.get("login_button"):
        click_element(driver, site_data["login_button"])

    # Change to credentials iframe
    if site_data.get("iframe_credentials"):
        change_frame(driver, site_data["iframe_credentials"])

    # Insert and submit credentials
    if site_data.get("user_input"):
        click_element(driver, site_data["user_input"])
        insert_credential(driver, username, site_data["user_input"])
    if site_data.get("second_submit_button") and site_data.get(
        "submit_button"
    ):
        scroll_to_element(driver, site_data["submit_button"])
        click_element(driver, site_data["submit_button"])
    if site_data.get("password_input"):
        click_element(driver, site_data["password_input"])
        insert_credential(driver, password, site_data["password_input"])
    if site_data.get("second_submit_button"):
        scroll_to_element(driver, site_data["second_submit_button"])
        click_element(driver, site_data["second_submit_button"])
    elif site_data.get("submit_button"):
        scroll_to_element(driver, site_data["submit_button"])
        click_element(driver, site_data["submit_button"])
    driver.switch_to.default_content()


def logout_paywalled_website(driver, site_data):
    # Go to profile section
    if site_data.get("profile_section"):
        click_element(driver, site_data["profile_section"])

    # Change to logout iframe
    if site_data.get("iframe_logout"):
        change_frame(driver, site_data["iframe_logout"])

    # Logout
    if site_data.get("logout_button"):
        click_element(driver, site_data["logout_button"])


"""
# Site dredentials
with open("newspapers_credentials.json", "r") as file:
    creds = json.load(file)
username = creds["newspapers"]["newspaper32"]["user_email"]
password = creds["newspapers"]["newspaper32"]["password"]

# Site data
with open("newspapers_data.json", "r") as file:
    sites = json.load(file)
site_data = sites["newspapers"]["newspaper32"]
name = site_data["name"]

# Initialization
driver = webdriver.Chrome()
driver.get(site_data["link"])
driver.maximize_window()

try:
    logger.info(f"Running code on website: {name}")
    login_paywalled_website(driver, username, password, site_data)
    logout_paywalled_website(driver, site_data)
    logger.info(f"Process successful on website: {name}")
except Exception:
    logger.error(f"Error on website: {name}")

time.sleep(60)
"""
