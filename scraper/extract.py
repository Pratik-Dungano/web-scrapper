"""
extract.py
Handles fetching web pages and extracting company information.
"""
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import re
from scraper.errors import NetworkError, DataExtractionError
import tldextract
import os
from dotenv import load_dotenv
from scraper.dynamic import fetch_dynamic_page
from scraper import utils
import time
from tqdm import tqdm

load_dotenv()  # For demo only; use env var in production

SOCIAL_PLATFORMS = [
    ("linkedin", "linkedin.com"),
    ("twitter", "twitter.com"),
    ("facebook", "facebook.com"),
    ("instagram", "instagram.com")
]

# Common tech stack keywords
TECH_KEYWORDS = [
    'react', 'angular', 'vue', 'django', 'flask', 'spring', 'node', 'express', 'ruby on rails',
    'laravel', 'wordpress', 'drupal', 'magento', 'shopify', 'firebase', 'aws', 'azure', 'gcp',
    'docker', 'kubernetes', 'mysql', 'postgresql', 'mongodb', 'redis', 'graphql', 'typescript', 'javascript', 'python', 'java', 'php', 'c#', 'c++', 'go', 'swift', 'kotlin'
]

US_STATE_ABBR = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
    'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
    'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
    'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri',
    'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
    'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
    'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
    'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'
}


def fetch_page(url: str, dynamic: bool = False, proxy: str = None) -> str:
    """
    Fetch the HTML content of a web page, using requests or Selenium if dynamic.
    Args:
        url (str): The URL to fetch.
        dynamic (bool): Whether to use dynamic fetching (Selenium).
        proxy (str): Proxy URL to use for the request.
    Returns:
        str: HTML content of the page.
    Raises:
        NetworkError: If the page cannot be fetched.
    """
    try:
        if dynamic:
            return fetch_dynamic_page(url)
        proxies = {"http": proxy, "https": proxy} if proxy else None
        resp = requests.get(url, timeout=10, proxies=proxies)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as e:
        raise NetworkError(f"Failed to fetch {url}: {e}")
    except Exception as e:
        raise NetworkError(f"Dynamic fetch failed for {url}: {e}")


def enrich_with_hunter(domain: str) -> dict:
    """
    Use Hunter.io Domain Search API to enrich company data.
    Args:
        domain (str): The company domain (e.g., 'python.org')
    Returns:
        dict: Enriched data (company, industry, emails, etc.)
    """
    api_key = os.environ.get("HUNTER_API_KEY", "")
    if not api_key:
        return {}
    url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={api_key}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json().get('data', {})
            state = data.get('state', '')
            # Map state abbreviation to full name if possible
            state_full = US_STATE_ABBR.get(state.upper(), state)
            return {
                'hunter_company': data.get('organization', ''),
                'hunter_industry': data.get('industry', ''),
                'hunter_emails': ', '.join([e.get('value', '') for e in data.get('emails', [])]),
                'hunter_country': data.get('country', ''),
                'hunter_state': state_full,
                'hunter_city': data.get('city', ''),
                'hunter_phone': data.get('phone_number', ''),
                'hunter_linkedin': data.get('linkedin', ''),
            }
        else:
            return {}
    except Exception:
        return {}


def extract_company_info(html: str, url: str, config: dict = None) -> Dict[str, str]:
    config = config or {}
    soup = BeautifulSoup(html, 'html.parser')
    # Company name
    name = None
    name_selector = config.get('company_name_selector')
    if name_selector:
        el = soup.select_one(name_selector)
        if el:
            name = el.get_text(strip=True)
    if not name:
        if soup.title and soup.title.string:
            name = soup.title.string.strip()
    if not name:
        og_site_name = soup.find('meta', property='og:site_name')
        if og_site_name and og_site_name.get('content'):
            name = og_site_name['content'].strip()
    website = url
    # Email
    email = None
    email_selector = config.get('email_selector')
    if email_selector:
        el = soup.select_one(email_selector)
        if el:
            email = el.get_text(strip=True)
    if not email:
        mailtos = soup.select('a[href^=mailto]')
        if mailtos:
            email = mailtos[0]['href'].replace('mailto:', '').split('?')[0]
    if not email:
        email_regex = config.get('email_regex', r'[\w\.-]+@[\w\.-]+')
        match = re.search(email_regex, html)
        if match:
            email = match.group(0)
    # Phone
    phone = None
    phone_selector = config.get('phone_selector')
    if phone_selector:
        el = soup.select_one(phone_selector)
        if el:
            phone = el.get_text(strip=True)
    if not phone:
        tels = soup.select('a[href^=tel]')
        if tels:
            phone = tels[0]['href'].replace('tel:', '').split('?')[0]
    if not phone:
        phone_regex = config.get('phone_regex', r'\+?\d[\d\s\-()]{7,}\d')
        match = re.search(phone_regex, html)
        if match:
            phone = match.group(0)
    # Social media profiles
    social = {}
    for plat, domain in SOCIAL_PLATFORMS:
        link = soup.find('a', href=re.compile(domain))
        social[plat] = link['href'] if link else ''
    # Address/location
    address = ''
    addr_tag = soup.find('address')
    if addr_tag:
        address = addr_tag.get_text(separator=' ', strip=True)
    else:
        match = re.search(r'\d{1,5} [\w .,-]+,? [A-Za-z ]+,? [A-Z]{2,} \d{5}', html)
        if match:
            address = match.group(0)
    # Description/tagline
    description = ''
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        description = meta_desc['content'].strip()
    if not description:
        og_desc = soup.find('meta', property='og:description')
        if og_desc and og_desc.get('content'):
            description = og_desc['content'].strip()
    # Year founded
    year_founded = ''
    match = re.search(r'Founded in (\d{4})', html, re.IGNORECASE)
    if match:
        year_founded = match.group(1)
    # Products/services (best effort: look for keywords)
    products = ''
    services = ''
    for section in soup.find_all(['section', 'div', 'p']):
        text = section.get_text(separator=' ', strip=True)
        if not products and re.search(r'products?|solutions?', text, re.IGNORECASE):
            products = text[:200]
        if not services and re.search(r'services?|offerings?', text, re.IGNORECASE):
            services = text[:200]
        if products and services:
            break
    # Industry/sector (look for keywords)
    industry = ''
    for tag in soup.find_all(['p', 'span', 'div']):
        text = tag.get_text(separator=' ', strip=True)
        if re.search(r'industry|sector|market', text, re.IGNORECASE):
            industry = text[:200]
            break
    # --- Level 3 fields ---
    # Tech stack: look for keywords in HTML and script/link tags
    tech_stack = set()
    lower_html = html.lower()
    for tech in TECH_KEYWORDS:
        if tech in lower_html:
            tech_stack.add(tech)
    # Also check script/link tags for tech hints
    for tag in soup.find_all(['script', 'link']):
        src = tag.get('src') or tag.get('href') or ''
        for tech in TECH_KEYWORDS:
            if tech in (src.lower()):
                tech_stack.add(tech)
    tech_stack_str = ', '.join(sorted(tech_stack))
    # Current projects/focus areas: look for keywords
    projects = ''
    for section in soup.find_all(['section', 'div', 'p']):
        text = section.get_text(separator=' ', strip=True)
        if re.search(r'project|initiative|focus|case study', text, re.IGNORECASE):
            projects = text[:200]
            break
    # Competitors: look for sections with 'competitor', 'alternatives', 'vs', or company names
    competitors = ''
    for section in soup.find_all(['section', 'div', 'ul', 'ol']):
        text = section.get_text(separator=' ', strip=True)
        if re.search(r'competitor|alternative|vs\.?|compared to', text, re.IGNORECASE):
            competitors = text[:200]
            break
    # Market positioning: look for keywords
    market_position = ''
    for tag in soup.find_all(['p', 'span', 'div']):
        text = tag.get_text(separator=' ', strip=True)
        if re.search(r'leader|challenger|innovator|market position', text, re.IGNORECASE):
            market_position = text[:200]
            break
    if not name and not email and not phone:
        raise DataExtractionError("No company info found on page.")
    # Extract domain from website URL
    ext = tldextract.extract(website)
    domain = f"{ext.domain}.{ext.suffix}" if ext.domain and ext.suffix else ''
    hunter_data = enrich_with_hunter(domain) if domain else {}
    result = {
        'company_name': name or '',
        'website': website,
        'email': email or '',
        'phone': phone or '',
        'linkedin': social['linkedin'],
        'twitter': social['twitter'],
        'facebook': social['facebook'],
        'instagram': social['instagram'],
        'address': address,
        'description': description,
        'year_founded': year_founded,
        'products': products,
        'services': services,
        'industry': industry,
        'tech_stack': tech_stack_str,
        'projects': projects,
        'competitors': competitors,
        'market_position': market_position
    }
    result.update(hunter_data)
    return result


def process_urls(urls: List[str], dynamic: bool = False, delay: list = [1.0, 3.0], proxies: list = None, config: dict = None) -> List[Dict[str, str]]:
    results = []
    proxy_list = proxies or []
    proxy_idx = 0
    errors = 0
    utils.log_info(f"Processing {len(urls)} URLs...")
    for url in tqdm(urls, desc="Scraping", unit="url"):
        try:
            proxy = proxy_list[proxy_idx % len(proxy_list)] if proxy_list else None
            html = fetch_page(url, dynamic=dynamic, proxy=proxy)
            info = extract_company_info(html, url, config=config)
            results.append(info)
            utils.log_info(f"SUCCESS: {url}")
            time.sleep(utils.get_delay(delay[0], delay[1]))
            proxy_idx += 1
        except (NetworkError, DataExtractionError) as e:
            errors += 1
            utils.log_info(f"ERROR: {url} - {e}")
            continue
    utils.log_info(f"Summary: {len(results)} successful, {errors} errors, {len(urls)} total.")
    print(f"\nSummary: {len(results)} successful, {errors} errors, {len(urls)} total.")
    return results
