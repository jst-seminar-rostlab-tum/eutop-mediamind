import argparse
import logging
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from app.services.hardcoded_login import hardcoded_login, hardcoded_logout

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Login to a specified newspaper or all newspapers.'
    )
    parser.add_argument(
        'newspaper_key',
        type=str, nargs='?',
        help='Key of the newspaper to log in (optional).'
    )
    args = parser.parse_args()

    if args.newspaper_key:
        key = args.newspaper_key
        logger.info(f"Trying login for {key}.")
        driver = webdriver.Chrome()
        wait = WebDriverWait(driver, 5)
        newspaper = hardcoded_login(driver, wait, key)
        if newspaper:
            logger.info(f"Login for {key} successful.")
            time.sleep(3)
            logout = hardcoded_logout(driver, wait, newspaper)
            if logout:
                logger.info(f"Logout for {key} successful.")
        else:
            logger.error(f"Login for {key} failed.")
        time.sleep(300)
        driver.quit()
