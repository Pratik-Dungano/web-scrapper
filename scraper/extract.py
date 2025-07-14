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

HUNTER_API_KEY = "1d957682afa00e4040e2fd7f07b197ae17373002"  # For demo only; use env var in production

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


def fetch_page(url: str) -> str:
    """
    Fetch the HTML content of a web page.
    Args:
        url (str): The URL to fetch.
    Returns:
        str: HTML content of the page.
    Raises:
        NetworkError: If the page cannot be fetched.
    """
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as e:
        raise NetworkError(f"Failed to fetch {url}: {e}")


def enrich_with_hunter(domain: str) -> dict:
    """
    Use Hunter.io Domain Search API to enrich company data.
    Args:
        domain (str): The company domain (e.g., 'python.org')
    Returns:
        dict: Enriched data (company, industry, emails, etc.)
    """
    url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={HUNTER_API_KEY}"
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


def extract_company_info(html: str, url: str) -> Dict[str, str]:
    """
    Extract company name, website, and contact info from HTML content.
    Args:
        html (str): HTML content of the page.
        url (str): The URL of the page (for context).
    Returns:
        Dict[str, str]: Extracted information (company name, website, email, phone).
    Raises:
        DataExtractionError: If required data cannot be extracted.
    """
    soup = BeautifulSoup(html, 'html.parser')
    # Company name
    name = None
    if soup.title and soup.title.string:
        name = soup.title.string.strip()
    if not name:
        og_site_name = soup.find('meta', property='og:site_name')
        if og_site_name and og_site_name.get('content'):
            name = og_site_name['content'].strip()
    website = url
    # Email
    email = None
    mailtos = soup.select('a[href^=mailto]')
    if mailtos:
        email = mailtos[0]['href'].replace('mailto:', '').split('?')[0]
    if not email:
        match = re.search(r'[\w\.-]+@[\w\.-]+', html)
        if match:
            email = match.group(0)
    # Phone
    phone = None
    tels = soup.select('a[href^=tel]')
    if tels:
        phone = tels[0]['href'].replace('tel:', '').split('?')[0]
    if not phone:
        match = re.search(r'\+?\d[\d\s\-()]{7,}\d', html)
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


def process_urls(urls: List[str]) -> List[Dict[str, str]]:
    """
    Process a list of URLs: fetch each page and extract company info.
    Args:
        urls (List[str]): List of URLs to process.
    Returns:
        List[Dict[str, str]]: List of extracted company info dicts.
    """
    results = []
    for url in urls:
        try:
            html = fetch_page(url)
            info = extract_company_info(html, url)
            results.append(info)
        except (NetworkError, DataExtractionError) as e:
            # Could log or collect errors here if needed
            continue
    return results
