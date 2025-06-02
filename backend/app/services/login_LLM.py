import os
import logging
import json
import asyncio
import time
from pydantic import BaseModel
from crawl4ai import AsyncWebCrawler, BrowserConfig
from crawl4ai import CrawlerRunConfig, CacheMode, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from dotenv import load_dotenv
from typing import Optional
from selenium import webdriver
from app.services.testing_elements import click_element, click_shadow_element
from app.services.testing_elements import change_frame, scroll_to_element
from app.services.testing_elements import insert_credential
from app.services.testing_elements import logout_paywalled_website


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

instructions_login_section = (
    "Analyze the website and extract login elements. "
    "For each element, provide the XPath that would "
    "work with Selenium. "
    "Retrieve this elements if available:\n"
    "1. Shadow DOM which contains the cookies window\n"
    "2. iframe which contains the cookies window\n"
    "3. Accept cookies element\n"
    "4. Refuse notifications element\n"
    "5. Path to login element (for example, path to dropdown menu)\n"
    "6. Login element itself\n"
    "Only include elements that actually exist on the page. "
    "The XPaths should be robust and preferably use attributes like "
    "'id', 'name', or 'data-testid' when available, falling back to "
    "text content or other attributes when necessary."
)

instructions_credentials_section = (
    "Analyze the website and extract login elements. "
    "For each element, provide the XPath that would "
    "work with Selenium. "
    "Retrieve this elements if available:\n"
    "1. iframe containing login form\n"
    "2. Username/email input field\n"
    "3. Password input field\n"
    "4. Submit username and password element\n"
    "5. Second submit username and password element if it exists\n"
    "Only include elements that actually exist on the page. "
    "The XPaths should be robust and preferably use attributes like "
    "'id', 'name', or 'data-testid' when available, falling back to "
    "text content or other attributes when necessary."
)

instructions_logout_section = (
    "Analyze the website and extract logout elements. "
    "For each element, provide the XPath that would "
    "work with Selenium. "
    "Retrieve this elements if available:\n"
    "1. Profile section after login\n"
    "2. iframe containing the logout element\n"
    "3. Logout element\n"
    "Only include elements that actually exist on the page. "
    "The XPaths should be robust and preferably use attributes like "
    "'id', 'name', or 'data-testid' when available, falling back to "
    "text content or other attributes when necessary."
)


class NewspaperLoginElements(BaseModel):
    name: str
    link: str
    shadow_cookies: Optional[str] = None
    iframe_cookies: Optional[str] = None
    cookies_button: Optional[str] = None
    refuse_notifications: Optional[str] = None
    path_to_login_button: Optional[str] = None
    login_button: Optional[str] = None
    iframe_credentials: Optional[str] = None
    user_input: Optional[str] = None
    password_input: Optional[str] = None
    submit_button: Optional[str] = None
    second_submit_button: Optional[str] = None
    profile_section: Optional[str] = None
    iframe_logout: Optional[str] = None
    logout_button: Optional[str] = None


async def crawl_elements(url: str, name: str, instructions: str):
    llm_extraction_strategy = LLMExtractionStrategy(
        llm_config=LLMConfig(provider="openai/gpt-4o-mini",
                             api_token=os.getenv('OPENAI_API_KEY')),
        schema=NewspaperLoginElements.model_json_schema(),
        extraction_type="schema",
        instruction=(instructions),
        apply_chunking=True,
        chunk_token_threshold=2000,
        overlap_rate=0.1,
        input_format="html",
        extra_args={"temperature": 0.1, "max_tokens": 2000},
        verbose=True
    )

    browser_config = BrowserConfig(
        verbose=True,
        headless=True,
        viewport_width=1280,
        viewport_height=720
    )

    crawl_config = CrawlerRunConfig(
        extraction_strategy=llm_extraction_strategy,
        cache_mode=CacheMode.BYPASS,
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url=url, config=crawl_config)

        if result.success:
            extracted_data = json.loads(result.extracted_content)
            if isinstance(extracted_data, list):
                merged_data = {"name": name, "link": url}
                for item in extracted_data:
                    if isinstance(item, dict):
                        for key, value in item.items():
                            if value is not None and key not in [
                                    'name', 'link', 'error']:
                                merged_data[key] = value
                return merged_data
            else:
                extracted_data['name'] = name
                extracted_data['link'] = url
                return extracted_data
        else:
            logger.error(f"Error crawling {url}: {result.error_message}")
            return None


async def add_page(name, url):
    try:
        with open('newspapers_data.json', 'r') as file:
            newspapers = json.load(file)
    except FileNotFoundError:
        newspapers = {}

    new_key = f"newspaper{len(newspapers)+1}"
    newspapers[new_key] = {"name": name, "link": url}

    logger.info(f"Crawling {name} for login elements...")
    login_result = await crawl_elements(url, name, instructions_login_section)

    if login_result:
        # Update only existing elements
        for key, value in login_result.items():
            if value is not None and key not in ['name', 'link']:
                newspapers[new_key][key] = value

        with open('newspapers_data.json', 'w') as file:
            json.dump(newspapers, file, indent=2, ensure_ascii=False)

        logger.info(f"Successfully added elements for {name}")
    else:
        logger.error(f"Failed to extract elements from {url}")

    driver = webdriver.Chrome()
    driver.get(url)
    driver.maximize_window()

    print("---------------------------")
    print(newspapers[new_key])

    # Change to cookies iframe
    if (newspapers[new_key].get("iframe_cookies")):
        change_frame(driver, newspapers[new_key]["iframe_cookies"])

    # Accept cookies
    if (newspapers[new_key].get("shadow_cookies")
            and newspapers[new_key].get("cookies_button")):
        click_shadow_element(
            driver,
            newspapers[new_key]["cookies_button"],
            newspapers[new_key]["shadow_cookies"]
        )
    elif (newspapers[new_key].get("cookies_button")):
        click_element(driver, newspapers[new_key]["cookies_button"])
    driver.switch_to.default_content()

    # Remove notifications window
    if (newspapers[new_key].get("refuse_notifications")):
        click_element(driver, newspapers[new_key]["refuse_notifications"])

    # Go to login section
    if (newspapers[new_key].get("path_to_login_button")):
        click_element(driver, newspapers[new_key]["path_to_login_button"])
    if (newspapers[new_key].get("login_button")):
        click_element(driver, newspapers[new_key]["login_button"])

    logger.info(f"Crawling {name} for credentials elements...")
    credentials_result = await crawl_elements(
        url, name, instructions_credentials_section
    )

    if credentials_result:
        for key, value in credentials_result.items():
            if value is not None and key not in ['name', 'link']:
                newspapers[new_key][key] = value

        with open('newspapers_data.json', 'w') as file:
            json.dump(newspapers, file, indent=2, ensure_ascii=False)

        logger.info(f"Successfully added credential elements for {name}")
    else:
        logger.error(f"Failed to extract credential elements from {url}")

    if newspapers[new_key].get("iframe_credentials"):
        change_frame(driver, newspapers[new_key]["iframe_credentials"])

    # Asumiendo que tienes credenciales de prueba
    username = "test_user"
    password = "test_password"

    # Insert and submit credentials
    if (newspapers[new_key].get("user_input")):
        click_element(driver, newspapers[new_key]["user_input"])
        insert_credential(driver, username, newspapers[new_key]["user_input"])
    if (newspapers[new_key].get("second_submit_button")
            and newspapers[new_key].get("submit_button")):
        scroll_to_element(driver, newspapers[new_key]["submit_button"])
        click_element(driver, newspapers[new_key]["submit_button"])
    if (newspapers[new_key].get("password_input")):
        click_element(driver, newspapers[new_key]["password_input"])
        insert_credential(
            driver, password, newspapers[new_key]["password_input"]
        )
    if (newspapers[new_key].get("second_submit_button")):
        scroll_to_element(driver, newspapers[new_key]["second_submit_button"])
        click_element(driver, newspapers[new_key]["second_submit_button"])
    elif (newspapers[new_key].get("submit_button")):
        scroll_to_element(driver, newspapers[new_key]["submit_button"])
        click_element(driver, newspapers[new_key]["submit_button"])
    driver.switch_to.default_content()

    logger.info(f"Crawling {name} for logout elements...")
    logout_result = await crawl_elements(
        url, name, instructions_logout_section
    )

    if logout_result:
        for key, value in logout_result.items():
            if value is not None and key not in ['name', 'link']:
                newspapers[new_key][key] = value

        with open('newspapers_data.json', 'w') as file:
            json.dump(newspapers, file, indent=2, ensure_ascii=False)

        logger.info(f"Successfully added logout elements for {name}")
    else:
        logger.error(f"Failed to extract logout elements from {url}")

    logout_paywalled_website(driver, newspapers[new_key])
    time.sleep(10)


asyncio.run(add_page("Platito", "https://www.platow.de/"))
