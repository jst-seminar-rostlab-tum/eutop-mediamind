import json
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def click_element(driver, wait, selector):
    try:
        time.sleep(1)
        if selector.startswith('class='):
            btn = wait.until(EC.element_to_be_clickable(
                (By.CLASS_NAME, selector.replace('class=', '').split()[0])
            ))
        elif selector.startswith('//'):
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
        else:
            btn = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, selector)
            ))
        try:
            btn.click()
            logger.info("Element clicked")
            return True
        except Exception:
            logger.info("Trying to click element with JavaScript")
            try:
                driver.execute_script(
                    "arguments[0].click();", btn
                )
                logger.info("Element clicked")
                return True
            except Exception as e:
                logger.error(f"Was not possible to click element: {e}")
                return False
    except Exception as e:
        logger.error(f"Element to click not found: {e}")
        return False


def click_shadow_element(driver, wait, element_selector, shadow_selector):
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


def change_frame(driver, wait, selector):
    try:
        iframe = wait.until(
            EC.presence_of_element_located((By.XPATH, selector))
        )
        driver.switch_to.frame(iframe)
        logger.info("Changed to iframe")
    except Exception as e:
        logger.error(f"Error when changing frames: {e}")


def scroll_to_element(driver, wait, selector):
    try:
        element = wait.until(
            EC.visibility_of_element_located((By.XPATH, selector)))
        driver.execute_script(
            "arguments[0].scrollIntoView({"
            "block: 'center', "
            "behavior: 'instant'"
            "});", element)
        time.sleep(1)

        logger.info("Scrolled to element")
        return True
    except Exception as e:
        logger.error(f"Failed to scroll to element: {e}")
        return False


def insert_credential(driver, wait, credential, input_selector):
    try:
        if input_selector.startswith('//'):
            input_field = wait.until(EC.presence_of_element_located(
                (By.XPATH, input_selector)
            ))
        else:
            input_field = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, input_selector)
            ))
        input_field.clear()
        input_field.send_keys(credential)
        time.sleep(1)
        logger.info("Credential inserted")
        return True
    except Exception as e:
        logger.warning(f"Could not insert credential: {e}")
        return False


def hardcoded_login(driver, wait, subscription_name, paper):

    # Load newspapers accounts
    with open('app/services/web_harvester/utils/newspapers_accounts.json', 'r') as f:
        accounts = json.load(f)

    # logger.info(f"Processing: {paper['name']}")
    # Find account credentials
    account = accounts.get(subscription_name)
    if not account:
        logger.error(f"No account found for key: {subscription_name}")
        return False
    username = account.get("user_email")
    password = account.get("password")
    if not username or not password:
        logger.error("No credentials found for this newspaper.")
        return False

    # Initialize newspaper website
    try:
        driver.get("https://epaper.sueddeutsche.de")
    except Exception as e:
        raise e
        # logger.error(f"No link provided for: {paper['name']}")
        return False

    driver.maximize_window()

    # Change to cookies iframe
    if (paper.get("iframe_cookies")):
        change_frame(driver, wait, paper["iframe_cookies"])

    # Accept cookies
    if (paper.get("shadow_cookies") and paper.get("cookies_button")):
        click_shadow_element(
            driver, wait, paper["cookies_button"], paper["shadow_cookies"]
        )
    elif (paper.get("cookies_button")):
        if not click_element(driver, wait, paper["cookies_button"]):
            try:
                logger.info("Searching for unregistered iframe")
                iframe = driver.find_element(
                    By.CSS_SELECTOR, "iframe[id^='sp_message_iframe']"
                )
                driver.switch_to.frame(iframe)
                time.sleep(1)
                click_element(driver, wait, paper["cookies_button"])
            except Exception:
                logger.warning("Was not possible to accept cookies")

    driver.switch_to.default_content()  # Always switch back to main context

    # Remove notifications window
    if (paper.get("refuse_notifications")):
        click_element(driver, wait, paper["refuse_notifications"])

    # Go to login section
    if (paper.get("path_to_login_button")):
        click_element(driver, wait, paper["path_to_login_button"])
    if (paper.get("login_button")):
        click_element(driver, wait, paper["login_button"])

    # Change to credentials iframe
    if (paper.get("iframe_credentials")):
        change_frame(driver, wait, paper["iframe_credentials"])

    # Insert and submit credentials
    if (paper.get("user_input")):
        click_element(driver, wait, paper["user_input"])
        insert_credential(driver, wait, username, paper["user_input"])
    if (paper.get("second_submit_button")
            and paper.get("submit_button")):
        scroll_to_element(driver, wait, paper["submit_button"])
        click_element(driver, wait, paper["submit_button"])
    if (paper.get("password_input")):
        click_element(driver, wait, paper["password_input"])
        insert_credential(driver, wait, password, paper["password_input"])
    if (paper.get("second_submit_button")):
        scroll_to_element(driver, wait, paper["second_submit_button"])
        if not click_element(driver, wait, paper["second_submit_button"]):
            logger.error("Failed to click second submit button")
            return False
    elif (paper.get("submit_button")):
        scroll_to_element(driver, wait, paper["submit_button"])
        if not click_element(driver, wait, paper["submit_button"]):
            logger.error("Failed to click submit button")
            return False

    driver.switch_to.default_content()  # Always switch back to main context

    return paper


def hardcoded_logout(driver, wait, paper):
    # Go to profile section
    if (paper.get("profile_section")):
        click_element(driver, wait, paper["profile_section"])

    # Change to logout iframe
    if (paper.get("iframe_logout")):
        change_frame(driver, wait, paper["iframe_logout"])

    # Logout
    if (paper.get("logout_button")):
        if not click_element(driver, wait, paper["logout_button"]):
            logger.error("Failed to logout from page")
            return False

    return True
