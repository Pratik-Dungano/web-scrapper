"""
dynamic.py
Fetches HTML content from JavaScript-rendered pages using Selenium.
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def fetch_dynamic_page(url: str, wait: int = 3) -> str:
    """
    Fetch the fully rendered HTML of a page using Selenium.
    Args:
        url (str): The URL to fetch.
        wait (int): Seconds to wait for JS to load.
    Returns:
        str: Rendered HTML content.
    """
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    try:
        driver.get(url)
        time.sleep(wait)  # Wait for JS to load
        html = driver.page_source
    finally:
        driver.quit()
    return html 