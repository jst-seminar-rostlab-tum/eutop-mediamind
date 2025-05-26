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


def accept_cookies(driver, wait, selector):
    if not selector:
        return
    try:
        if selector.startswith('class='):
            btn = wait.until(EC.element_to_be_clickable(
                (By.CLASS_NAME, selector.replace('class=', '').split()[0])))
        elif selector.startswith('//'):
            btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, selector)))
        else:
            btn = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, selector)))
        btn.click()
        print("Cookies accepted.")
    except Exception as e:
        print(f"Could not click cookie button: {e}")


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


def change_frame(driver, frame, site_name):
    try:
        f = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, frame))
        )
        driver.switch_to.frame(f)
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


def insert_credential(driver, cred, xpath_cred, site_name):
    try:
        input_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath_cred)))
        input_field.clear()
        input_field.send_keys(cred)

        logger.info(f"Credential inserted on {site_name}")
        return True
    except Exception as e:
        logger.warning(f"Trying second approach on {site_name}: {e}")
        try:
            input_login = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.NAME, xpath_cred))
            )
            input_field.clear()
            input_login.send_keys(cred)
        except Exception as e:
            logger.warning(f"Could not insert credential on {site_name}: {e}")
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
        try:
            clickable_element.click()
            logger.info(f"Button clicked on {site_name}")
            return True
        except Exception:
            logger.info(f"Trying to click button with JavaScript {site_name}")
            try:
                driver.execute_script(
                    "arguments[0].click();", clickable_element
                )
                logger.info(f"Button clicked on {site_name}")
                return True
            except Exception as e:
                logger.error(
                    f"Was not possible to click button on {site_name}: {e}"
                )
                return False
    except Exception as e:
        logger.error(f"Element to click not found on {site_name}: {e}")
        return False


with open("newspapers_complete.json", "r") as file:
    sites = json.load(file)
site = sites["newspapers"]["newspaper21"]  # HERE CHANGES

user = site["user_email"]
password = site["password"]

with open("newspapers_data.json", "r") as file:
    sites = json.load(file)
sitio = sites["newspapers"]["newspaper21"]  # HERE CHANGES

site_name = sitio["name"]
link = sitio["link"]
# iframe_c = sitio["iframe_cookies"]
# shadow = sitio["shadow"]
# cookies = sitio["cookies_button"]
# notifications = sitio["refuse_notifications"]
# login_button = sitio["login_button"]
# iframe = sitio["iframe"]
# user_input = sitio["user_input"]
# password_input = sitio["password_input"]
# submit = sitio["submit_button"]
# submit2 = sitio["submit_button2"]
# profile = sitio["profile_page"]
# iframe2 = sitio["iframe2"]
# logout = sitio["logout"]

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 15)
driver.get(link)
driver.maximize_window()


# click_element(driver, login_button, site_name)
# driver.switch_to.default_content()
# insert_credentials(
#    driver, user_input, password_input, user, password, site_name)
# click_element(driver, submit, site_name)

time.sleep(300)

driver.quit()

# QUOTIDIEN EUROPE
# click_element(driver, cookies, site_name)
# click_element(driver, login_button, site_name)
# click_element(driver, user_input, site_name)
# insert_credential(driver, user, user_input, site_name)
# insert_credential(driver, password, password_input, site_name)
# click_element(driver, submit, site_name)
# click_element(driver, profile, site_name)
# click_element(driver, logout, site_name)

# THE PIONEER
# change_frame(driver, iframe_c, site_name)
# click_element(driver, cookies, site_name)
# driver.switch_to.default_content()
# click_element(driver, login_button, site_name)
# time.sleep(2)
# change_frame(driver, iframe, site_name)
# insert_credential(driver, user, user_input, site_name)
# click_element(driver, submit, site_name)
# insert_credential(driver, password, password_input, site_name)
# click_element(driver, submit2, site_name)
# driver.switch_to.default_content()
# click_element(driver, profile, site_name)
# click_element(driver, logout, site_name)

# CONTEXTE
# click_element(driver, login_button, site_name)
# insert_credentials(
#    driver, user_input, password_input, user, password, site_name)
# click_element(driver, submit, site_name)
# click_element(driver, profile, site_name)
# click_element(driver, logout, site_name)

# BUSINESS INSIDER
# change_frame(driver, iframe_c, site_name)
# click_element(driver, cookies, site_name)
# time.sleep(3)
# driver.switch_to.default_content()
# click_element(driver, notifications, site_name)
# click_element(driver, profile, site_name)
# click_element(driver, login_button, site_name)
# change_frame(driver, iframe, site_name)
# time.sleep(2)
# insert_credentials(
#    driver, user_input, password_input, user, password, site_name)
# time.sleep(2)
# click_element(driver, submit, site_name)
# driver.switch_to.default_content()
# click_element(driver, profile, site_name)
# click_element(driver, logout, site_name)

# HORIZON
# shadow_host = WebDriverWait(driver, 10).until(
#    EC.presence_of_element_located((By.CSS_SELECTOR, shadow))
# )
# shadow_root = driver.execute_script(
#    "return arguments[0].shadowRoot", shadow_host)
# accept_button = shadow_root.find_element(
#    By.CSS_SELECTOR, cookies)
# accept_button.click()
# click_element(driver, login_button, site_name)
# insert_credentials(
#    driver, user_input, password_input, user, password, site_name)
# click_element(driver, submit, site_name)
# click_element(driver, profile, site_name)
# click_element(driver, logout, site_name)

# LE SOIR
# click_element(driver, cookies, site_name)
# click_element(driver, login_button, site_name)
# insert_credential(driver, user, user_input, site_name)
# click_element(driver, submit, site_name)
# insert_credential(driver, password, password_input, site_name)
# click_element(driver, submit, site_name)
# click_element(driver, profile, site_name)
# click_element(driver, logout, site_name)

# LEBENSMITTELZEITUNG
# shadow_host = WebDriverWait(driver, 10).until(
#    EC.presence_of_element_located((By.CSS_SELECTOR, shadow))
# )
# shadow_root = driver.execute_script(
#    "return arguments[0].shadowRoot", shadow_host)
# accept_button = shadow_root.find_element(
#    By.CSS_SELECTOR, cookies)
# accept_button.click()
# click_element(driver, login_button, site_name)
# insert_credentials(
#    driver, user_input, password_input, user, password, site_name)
# click_element(driver, submit, site_name)
# click_element(driver, profile, site_name)
# click_element(driver, logout, site_name)

# MACE MAGAZINE
# click_element(driver, login_button, site_name)
# insert_credentials(
#   driver, user_input, password_input, user, password, site_name)
# click_element(driver, submit, site_name)
# click_element(driver, profile, site_name)
# click_element(driver, logout, site_name)

# MEDIEN INSIDER ??????????
# change_frame(driver, iframe_c, site_name)
# click_element(driver, cookies, site_name)

# MEEDIA
# click_element(driver, cookies, site_name)
# click_element(driver, login_button, site_name)
# insert_credentials(
#   driver, user_input, password_input, user, password, site_name)
# scroll_to_element(driver, submit, site_name)
# click_element(driver, submit, site_name)
# click_element(driver, profile, site_name)
# click_element(driver, logout, site_name)

# PLATOW
# click_element(driver, cookies, site_name)
# click_element(driver, login_button, site_name)
# time.sleep(2)
# driver.switch_to.default_content()
# change_frame(driver, iframe, site_name)
# insert_credentials(
#   driver, user_input, password_input, user, password, site_name)
# scroll_to_element(driver, submit, site_name)
# click_element(driver, submit, site_name)
# click_element(driver, profile, site_name)
# change_frame(driver, iframe2, site_name)
# click_element(driver, logout, site_name)
