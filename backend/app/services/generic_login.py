import json
import logging
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

input_xpath_templates = [
    # '//input[contains(@id, "{keyword}")]',
    # '//input[contains(@name, "{keyword}")]',
    # '//input[contains(@placeholder, "{keyword}")]'
]

button_xpath_templates = [
    # '//button[contains(text(), "{keyword}")]',
    # '//button[contains(@id, "{keyword}")]',
    # '//button[contains(@name, "{keyword}")]',
    # '//button[contains(@class, "{keyword}")]'
]

link_xpath_templates = [
    # '//a[contains(@href, "{keyword}")]',
    # '//a[contains(text(), "{keyword}")]',
    # '//a[@title and contains(@title, "{keyword}")]'
]

login_page_keywords = [
    # 'Login',
    # 'login',
    # 'anmeldung',
    # 'anmelden'
]

profile_page_keywords = [
    # 'Profil',
    # 'profil',
    # 'profile',
    # 'Profile'
]

logout_keywords = [
    # 'Logout',
    # 'logout'
]

cookies_keywords = [
    # 'alle akzeptieren',
    # 'akzeptieren',
    # 'accept'
]

user_keywords = [
    # 'username'
]

password_keywords = [
    # 'password'
]

submit_keywords = [
    # 'Anmelden',
    # 'anmelden',
]


def find_element(driver, xpath_templates, keywords):
    for k in keywords:
        for template in xpath_templates:
            current_xpath = template.format(keyword=k)
            try:
                WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, current_xpath))
                )
                return current_xpath
            except Exception:
                continue
    return None


# CHANGES THIS
def change_frame(driver, frame, site_name):
    try:
        driver.switch_to.frame(frame)
        logger.info(f"Frame changed on {site_name}")
    except Exception as e:
        logger.error(f"Error when changing frames on {site_name}: {e}")


def insert_credentials(driver, user_xpath,
                       password_xpath, user, password, site_name):
    try:
        user_input_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, user_xpath)))
        user_input_field.clear()
        user_input_field.send_keys(user)

        password_input_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, password_xpath)))
        password_input_field.clear()
        password_input_field.send_keys(password)

        logger.info(f"Credentials inserted on {site_name}")
        return True
    except Exception as e:
        logger.warning(f"Could not insert credentials on {site_name}: {e}")
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


def click_element(driver, button_xpath, site_name):
    try:
        clickable_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, button_xpath)))
        clickable_element.click()
        logger.info(f"Button clicked on {site_name}")
        return True
    except Exception as e:
        logger.error(f"Error at clicking button on {site_name}: {e}")
        return False


def logging_newspaper(site):
    driver = webdriver.Chrome()

    site_name = site["name"]
    user = site["user_email"]
    password = site["password"]
    link = site["link"]

    driver.get(link)
    driver.maximize_window()

    # Accept cookies
    cookies_button = find_element(driver,
                                  button_xpath_templates, cookies_keywords)
    click_element(driver, cookies_button, site_name)

    # Go to log in page
    login_page = find_element(driver,
                              link_xpath_templates, login_page_keywords)
    click_element(driver, login_page, site_name)

    # Insert user credentials
    user_xpath = find_element(
        driver, input_xpath_templates, user_keywords)
    password_xpath = find_element(
        driver, input_xpath_templates, password_keywords)

    if user_xpath is None or password_xpath is None:
        logger.info(f"Could not find login fields for {site_name}."
                    "Trying to locate inside iframe...")
        iframes = driver.find_elements(By.TAG_NAME, "iframe")

        for iframe in iframes:
            driver.switch_to.default_content()

            change_frame(driver, iframe, site_name)

            user_xpath = find_element(
                driver, input_xpath_templates, user_keywords)
            password_xpath = find_element(
                driver, input_xpath_templates, password_keywords)

            if insert_credentials(driver, user_xpath, password_xpath,
                                  user, password, site_name):
                # driver.switch_to.default_content()
                break
    else:
        insert_credentials(driver, user_xpath, password_xpath, user,
                           password, site_name)

    # Submit credentials
    submit_button_xpath = find_element(driver, button_xpath_templates,
                                       submit_keywords)
    if submit_button_xpath:
        scroll_to_element(driver, submit_button_xpath, site_name)
        click_element(driver, submit_button_xpath, site_name)
    else:
        logger.warning(f"Submit button not found on {site_name}")
    time.sleep(3)

    driver.switch_to.default_content()

    # Log out
    profile_page = find_element(driver,
                                link_xpath_templates, profile_page_keywords)
    click_element(driver, profile_page, site_name)
    time.sleep(3)
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    for iframe in iframes:
        driver.switch_to.default_content()
        change_frame(driver, iframe, site_name)
        logout_button = find_element(
            driver, link_xpath_templates, logout_keywords)
        if click_element(driver, logout_button, site_name):
            break

    time.sleep(20)
    driver.quit()


with open("newspapers.json", "r") as file:
    sites = json.load(file)
site = sites["newspapers"]["newspaper1"]
logging_newspaper(site)

# Pendientes
# Borrar sesion
# Velocidad de navegacion
