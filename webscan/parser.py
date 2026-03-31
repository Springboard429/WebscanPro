import re
from urllib.parse import urlparse, urljoin, parse_qs, urlunparse
from typing import List

def normalize_url(url: str, base: str = None) -> str:
    if base and not url.startswith(('http://', 'https://')):
        url = urljoin(base, url)
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, parsed.query, ''))

def get_base_url(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"

def is_same_domain(url1: str, url2: str) -> bool:
    return urlparse(url1).netloc == urlparse(url2).netloc

def should_exclude(url: str, patterns: List[str]) -> bool:
    return any(re.search(p, url, re.I) for p in patterns)
