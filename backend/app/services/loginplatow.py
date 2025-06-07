import json
import logging
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Load credentials from JSON
with open("app/services/newspapers_accounts.json", "r") as f:
    accounts = json.load(f)
platow_credentials = accounts.get("platow", {})
username = platow_credentials.get("username")
password = platow_credentials.get("password")

# Start browser
driver = webdriver.Chrome()
driver.get("https://www.platow.de")

# Wait for page to load (adjust as needed)
time.sleep(1)

try:
    close_svg_btn = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "brlbs-cmpnt-w-4"))
    )
    close_svg_btn.click()
    logger.info("Cookie modal closed via SVG.")
except TimeoutException:
    logger.warning("SVG close button not found or already closed.")

# Click login (if needed) Doesnt work
login_button = WebDriverWait(driver, 2).until(
    EC.element_to_be_clickable(
        (
            By.XPATH,
            "//a[@href='https://www.platow.de/anmeldung/"
            "?redirectUrl=https%3A%2F%2Fwww.platow.de%2F']",
        )
    )
)
login_button.click()
time.sleep(3)


# Enter credentials in new form
WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.NAME, "login_form[_username]"))
).send_keys(username)

driver.find_element(By.NAME, "login_form[_password]").send_keys(password)

# Optional: click "Angemeldet bleiben" checkbox
try:
    driver.find_element(By.ID, "login_form_rememberMe").click()
except Exception as e:
    logger.warning(f"Could not click remember me checkbox: {str(e)}")

# Submit the form via JavaScript to bypass disabled button issue
driver.execute_script(
    "document.querySelector('form[name=login_form]').submit();"
)

# Optional: wait and check login success
time.sleep(2)

# You're in – proceed to scrape or navigate as needed

# Close the browser when done
# driver.quit()
