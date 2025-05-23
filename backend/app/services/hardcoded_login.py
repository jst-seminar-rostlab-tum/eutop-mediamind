import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def accept_cookies(driver, wait, selector):
    if not selector:
        return
    try:
        # Try switching to the iframe if it exists
        try:
            iframe = driver.find_element(By.CSS_SELECTOR, "iframe[id^='sp_message_iframe']")
            driver.switch_to.frame(iframe)
            print("Switched to cookie iframe.")
        except Exception:
            pass  # No iframe, continue

        if selector.startswith('class='):
            btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, selector.replace('class=', '').split()[0])))
        elif selector.startswith('//'):
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
        else:
            btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
        btn.click()
        print("Cookies accepted.")

        driver.switch_to.default_content()  # Always switch back to main context
    except Exception as e:
        print(f"Could not click cookie button: {e}")
        try:
            driver.switch_to.default_content()
        except:
            pass


def click_login(driver, wait, selector):
    if not selector:
        return
    try:
        if selector.startswith('//'):
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
        else:
            btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
        btn.click()
        print("Login button clicked.")
    except Exception as e:
        print(f"Could not click login button: {e}")

#email_sel, pass_sel = Selectors to locate the email and password input fields on the webpage
def fill_credentials(driver, wait, email_sel, pass_sel, email, password):
    if not email_sel or not pass_sel:
        return
    try:
        if email_sel.startswith('//'):
            email_input = wait.until(EC.presence_of_element_located((By.XPATH, email_sel)))
        else:
            email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, email_sel)))
        email_input.send_keys(email)

        if pass_sel.startswith('//'):
            pass_input = wait.until(EC.presence_of_element_located((By.XPATH, pass_sel)))
        else:
            pass_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, pass_sel)))
        pass_input.send_keys(password)

        print("Filled in credentials.")
    except Exception as e:
        print(f"Could not fill in credentials: {e}")

def submit_login(driver, wait, selector):
    if not selector:
        return
    try:
        if selector.startswith('//'):
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
        else:
            btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
        btn.click()
        input("Press Enter to close browser:")
        print("Login submitted.")
    except Exception as e:
        print(f"Could not submit login: {e}")

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 5)

# Load newspapers data
with open('app/services/newspapers_data.json', 'r') as f:
    data = json.load(f)

# Load newspapers accounts
with open('app/services/newspapers_accounts.json', 'r') as f:
    accounts = json.load(f)

# Add any keys you want to test, test one by one
whitelist = ["newspaper8"]  
    
for key, paper in data['newspapers'].items():
    if key not in whitelist:
        continue
    print(f"\nProcessing: {paper['name']}")
    try:
        driver.get(paper['link'])

        # find account by matching link
        email = "didnt_find@email.com"
        password = "didnt_find_password"
        for acc in accounts.values():
            if acc.get("link") == paper.get("link"):
                email = acc.get("email", email)
                password = acc.get("password", password)
                break

        print(f"------------------------------")
        print(f"cookies_button: {paper.get('cookies_button', '')}")
        accept_cookies(driver, wait, paper.get('cookies_button', ''))
        print(f"------------------------------")

        print(f"login_button: {paper.get('login_button', '')}")
        click_login(driver, wait, paper.get('login_button', ''))
        print(f"------------------------------")


        print(f"email_input:", email)
        fill_credentials(driver, wait, paper.get('user_input', ''), paper.get('password_input', ''), email, password)
        print(f"------------------------------")

        print(f"submit_button: {paper.get('submit_button', '')}")
        submit_login(driver, wait, paper.get('submit_button', ''))
        print(f"------------------------------")
    except Exception as e:
        print(f"Failed to process {paper['name']}: {e}")

# driver.quit()