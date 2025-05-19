import asyncio
import urllib.parse
import nest_asyncio
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import CrawlerRunConfig
from datetime import datetime

nest_asyncio.apply()

async def extract_news_links(search_url):
    crawler = AsyncWebCrawler()
    result = await crawler.arun(search_url)
    soup = BeautifulSoup(result.html, "html.parser")
    
    # Add debug information
    print("\n🔍 Page Content Analysis:")
    print(f"Page Title: {soup.title.string if soup.title else 'No Title'}")
    
    # Find search results area
    search_results = soup.find_all('article')  # Welt.de search results are usually in article tags
    print(f"\nFound {len(search_results)} search results")
    
    article_links = []
    for article in search_results:
        # Find article links
        link = article.find('a')
        if link and link.get('href'):
            href = link.get('href')
            if href.startswith('/'):  # Handle relative paths
                href = f"https://www.welt.de{href}"
            
            # Check if it's an economic article
            is_economic = '/wirtschaft/' in href
            if href not in article_links:
                article_links.append({
                    'url': href,
                    'is_economic': is_economic
                })
                print(f"Found article link: {href} {'(Economic)' if is_economic else ''}")
    
    print(f"\nFound {len(article_links)} valid article links")
    if article_links:
        print("Article Links List:")
        for i, article in enumerate(article_links[:5], 1):
            print(f"{i}. {article['url']} {'(Economic)' if article['is_economic'] else ''}")
    
    return article_links[:5]

async def extract_article_content(url):
    crawler = AsyncWebCrawler()
    result = await crawler.arun(url)
    soup = BeautifulSoup(result.html, "html.parser")
    
    # Extract article title
    title = soup.find('h2')
    title_text = title.text.strip() if title else "No Title"
    
    # Extract publication date
    date = soup.find('time')
    date_text = date.text.strip() if date else "No Date"
    
    # Extract article category
    category = "Unknown"
    if '/wirtschaft/' in url:
        category = "Economy"
    elif '/politik/' in url:
        category = "Politics"
    elif '/sport/' in url:
        category = "Sports"
    
    # Extract article content
    article_content = []
    content_div = soup.find('div', class_='c-article-text')  # Welt.de article content is usually in this class
    if content_div:
        paragraphs = content_div.find_all('p')
        for p in paragraphs:
            text = p.text.strip()
            if text:
                article_content.append(text)
    
    return {
        'title': title_text,
        'date': date_text,
        'category': category,
        'content': '\n'.join(article_content)
    }

async def main():
    search_url = "https://www.welt.de/suche?q=bmw"
    article_links = await extract_news_links(search_url)

    run_config = CrawlerRunConfig()
    async with AsyncWebCrawler(config=None) as crawler:
        for article in article_links:
            print(f"\n🔗 Crawling article: {article['url']}")
            
            # Extract article content
            article_data = await extract_article_content(article['url'])
            print(f"\nTitle: {article_data['title']}")
            print(f"Date: {article_data['date']}")
            print(f"Category: {article_data['category']}")
            print("\nArticle Content:")
            print(article_data['content'][:500] + "...")  # Only show first 500 characters
            
            # Check if contains keyword
            if 'bmw' in article_data['content'].lower():
                print("\n✅ Article contains 'bmw' keyword")
            else:
                print("\n⚠️ Article does not contain 'bmw' keyword")

asyncio.run(main())
