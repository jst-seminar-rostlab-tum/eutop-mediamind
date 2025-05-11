from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Für Tests und lokale Entwicklung per Default sqlite
    DATABASE_URL: str = "sqlite:///./test.db"
    # User-Agent für Web-Scraping
    USER_AGENT: str = "MyScraperBot/1.0"
    # Optional: Pfad zum Selenium WebDriver
    SELENIUM_DRIVER_PATH: str = "./chromedriver"

    API_KEY_NEWS_API_AI: str = "0dd48ba4-0539-4d0f-9962-894ae442092c"

    class Config:
        env_file = ".env"