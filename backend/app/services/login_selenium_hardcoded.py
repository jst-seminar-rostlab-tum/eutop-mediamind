import json
import logging
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def accept_cookies(driver, cookies_button, site_name):
    try:
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, cookies_button))
        )
        accept_button.click()
        logger.info(f"Cookies accepted on {site_name}")
    except Exception as e:
        logger.error(f"Error, cookies not accepted on {site_name}: {e}")


def click_login_button(driver, login_button, site_name):
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                (By.XPATH, login_button))).click()
        logger.info(f"Login button clicked on {site_name}")
    except Exception as e:
        logger.error(f"Error clicking login button on {site_name}: {e}")


def change_frame(driver, frame, site_name):
    try:
        WebDriverWait(driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.XPATH, frame)))
        logger.info(f"Frame changed on {site_name}")
    except Exception as e:
        logger.error(f"Error when changing frames on {site_name}: {e}")


def insert_credentials(driver, user, user_xpath,
                       password, password_xpath, site_name):
    try:
        user_input_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, user_xpath)))
        user_input_field.clear()
        user_input_field.send_keys(user)

        password_input_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, password_xpath)))
        password_input_field.clear()
        password_input_field.send_keys(password)

        logger.info(f"Credentials sent on {site_name}")
        return True
    except Exception as e:
        logger.warning(f"Could not find input fields on {site_name}: {e}")
        return False


def scroll_to_element(driver, element_xpath, site_name):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, element_xpath)))
        driver.execute_script(
            "arguments[0].scrollIntoView({"
            "block: 'center', "
            "behavior: 'instant'"
            "});", element)
        time.sleep(3)

        logger.info(f"Scrolled to element in {site_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to scroll to element in {site_name}: {e}")
        return False


def submit_credentials(driver, submit_button_xpath, site_name):
    try:
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, submit_button_xpath)))
        submit_button.click()
        logger.info(f"Submission completed on {site_name}")
    except Exception as e:
        logger.error(f"Submission failed on {site_name}: {e}")


def logging_newspaper(site):
    driver = webdriver.Chrome()
    driver.get(site["link"])
    driver.maximize_window()
    accept_cookies(driver, site["cookies_button"], site["name"])
    click_login_button(driver, site["login_button"], site["name"])
    if "iframe" in site and site["iframe"]:
        change_frame(driver, site["iframe"], site["name"])
    insert_credentials(
        driver, site["user_email"], site["user_input"],
        site["password"], site["password_input"], site["name"])
    scroll_to_element(driver, site["submit_button"], site["name"])
    submit_credentials(driver, site["submit_button"], site["name"])
    time.sleep(15)
    driver.quit()


with open("newspapers_complete.json", "r") as file:
    sites = json.load(file)
site = sites["newspapers"]["newspaper32"]
logging_newspaper(site)

# Borrar sesiones
