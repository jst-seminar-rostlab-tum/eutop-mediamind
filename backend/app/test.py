import asyncio
from newsplease import NewsPlease
from newspaper import Article
from sqlmodel import Session
from app.core.db import engine
from app.repositories.subscription_repository import SubscriptionRepository
import newspaper
import trafilatura
import json

if __name__ == "__main__":
    downloaded = trafilatura.fetch_url(
        'https://www.welt.de/wirtschaft/article256174234/Tesla-Verkaeufe-in-Europa-halbieren-sich-mehrere-Hersteller-ueberholen-den-E-Auto-Pionier.html')
    result = trafilatura.extract(downloaded, output_format='json')
    a = json.loads(result)
    print(a)
