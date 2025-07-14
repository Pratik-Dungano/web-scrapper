"""
crawler.py
Handles pagination and URL discovery for web scraping.
"""
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
from scraper.errors import NetworkError

def crawl_pagination(start_url: str, max_pages: int = 10) -> list:
    """
    Crawl paginated links starting from start_url.
    Args:
        start_url (str): The initial URL to start crawling.
        max_pages (int): Maximum number of pages to follow.
    Returns:
        list: List of discovered paginated URLs (including start_url).
    """
    urls = [start_url]
    current_url = start_url
    for _ in range(max_pages - 1):
        try:
            resp = requests.get(current_url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Look for 'next' link (common patterns)
            next_link = (soup.find('a', string=re.compile(r'next', re.I)) or
                         soup.find('a', rel='next'))
            if not next_link or not next_link.get('href'):
                break
            next_url = urljoin(current_url, next_link['href'])
            if next_url in urls:
                break
            urls.append(next_url)
            current_url = next_url
        except Exception:
            break
    return urls 