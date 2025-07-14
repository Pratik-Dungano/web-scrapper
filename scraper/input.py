"""
input.py
Handles user input: CLI argument parsing, URL validation, and reachability checks.
"""
from typing import List, Union
import argparse
import re
import requests
from scraper.errors import InvalidURLError, URLUnreachableError


def parse_args() -> Union[str, List[str]]:
    """
    Parse command-line arguments to get a search query or a list of seed URLs.
    Returns:
        str or List[str]: The search query or list of URLs provided by the user.
    """
    parser = argparse.ArgumentParser(description="Web Scraper Input")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--query', type=str, help='Search query to generate URLs')
    group.add_argument('--urls', nargs='+', help='List of seed URLs')
    args = parser.parse_args()
    if args.query:
        return args.query
    else:
        return args.urls


def validate_urls(urls: List[str]) -> List[str]:
    """
    Validate the format of each URL in the list.
    Args:
        urls (List[str]): List of URLs to validate.
    Returns:
        List[str]: List of valid URLs.
    Raises:
        InvalidURLError: If any URL is invalid.
    """
    url_regex = re.compile(
        r'^(https?://)?'  # http:// or https://
        r'([\w.-]+)\.([a-zA-Z]{2,})(:[0-9]+)?'  # domain
        r'(/[\w\-./?%&=]*)?$', re.IGNORECASE)
    valid_urls = []
    for url in urls:
        if not url.lower().startswith(('http://', 'https://')):
            url = 'http://' + url  # Default to http if scheme missing
        if not url_regex.match(url):
            raise InvalidURLError(f"Invalid URL format: {url}")
        valid_urls.append(url)
    return valid_urls


def check_reachability(urls: List[str]) -> List[str]:
    """
    Check if each URL is reachable (HTTP 200 OK).
    Args:
        urls (List[str]): List of URLs to check.
    Returns:
        List[str]: List of reachable URLs.
    Raises:
        URLUnreachableError: If any URL is not reachable.
    """
    reachable = []
    for url in urls:
        try:
            resp = requests.head(url, timeout=5, allow_redirects=True)
            if resp.status_code == 200:
                reachable.append(url)
            else:
                raise URLUnreachableError(f"URL not reachable (status {resp.status_code}): {url}")
        except requests.RequestException as e:
            raise URLUnreachableError(f"URL not reachable: {url} ({e})")
    return reachable
