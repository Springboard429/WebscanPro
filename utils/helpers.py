"""
Helper functions for WebScanPro.

This module contains various utility functions used throughout the application.
"""

import re
import string
import random
import ipaddress
import socket
import urllib.parse
import hashlib
import json
import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse, urljoin, parse_qs, urlencode, parse_qsl

# Set up logger
logger = logging.getLogger('webscanpro.helpers')

def is_valid_url(url: str) -> bool:
    """
    Check if a string is a valid URL.
    
    Args:
        url: The URL to validate
        
    Returns:
        bool: True if the URL is valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except ValueError:
        return False

def normalize_url(url: str) -> str:
    """
    Normalize a URL by adding a scheme if missing and removing fragments.
    
    Args:
        url: The URL to normalize
        
    Returns:
        str: Normalized URL
    """
    if not url:
        return url
    
    # Add http:// if no scheme is provided
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    # Parse the URL
    parsed = urlparse(url)
    
    # Remove fragments and query parameters for normalization
    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    
    # Remove trailing slash for consistency
    if normalized.endswith('/') and len(normalized) > 1:
        normalized = normalized.rstrip('/')
    
    return normalized

def get_domain(url: str) -> str:
    """
    Extract the domain from a URL.
    
    Args:
        url: The URL to extract the domain from
        
    Returns:
        str: The domain name
    """
    try:
        domain = urlparse(url).netloc
        # Remove port number if present
        if ':' in domain:
            domain = domain.split(':')[0]
        return domain
    except Exception as e:
        logger.error(f"Error extracting domain from {url}: {e}")
        return ""

def is_same_domain(url1: str, url2: str) -> bool:
    """
    Check if two URLs belong to the same domain.
    
    Args:
        url1: First URL
        url2: Second URL
        
    Returns:
        bool: True if both URLs have the same domain, False otherwise
    """
    return get_domain(url1) == get_domain(url2)

def generate_random_string(length: int = 10, charset: str = None) -> str:
    """
    Generate a random string of specified length.
    
    Args:
        length: Length of the random string
        charset: Character set to use (default: letters + digits)
        
    Returns:
        str: Random string
    """
    if charset is None:
        charset = string.ascii_letters + string.digits
    return ''.join(random.choice(charset) for _ in range(length))

def md5_hash(data: str) -> str:
    """
    Calculate the MD5 hash of a string.
    
    Args:
        data: Input string
        
    Returns:
        str: MD5 hash of the input string
    """
    return hashlib.md5(data.encode('utf-8')).hexdigest()

def sha256_hash(data: str) -> str:
    """
    Calculate the SHA-256 hash of a string.
    
    Args:
        data: Input string
        
    Returns:
        str: SHA-256 hash of the input string
    """
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def is_ip_address(ip: str) -> bool:
    """
    Check if a string is a valid IP address.
    
    Args:
        ip: The string to check
        
    Returns:
        bool: True if the string is a valid IP address, False otherwise
    """
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def resolve_domain(domain: str) -> Optional[str]:
    """
    Resolve a domain name to its IP address.
    
    Args:
        domain: The domain name to resolve
        
    Returns:
        Optional[str]: The IP address if resolution is successful, None otherwise
    """
    try:
        return socket.gethostbyname(domain)
    except socket.gaierror:
        return None

def parse_http_headers(headers_str: str) -> Dict[str, str]:
    """
    Parse HTTP headers from a string to a dictionary.
    
    Args:
        headers_str: HTTP headers as a string
        
    Returns:
        Dict[str, str]: Dictionary of header names and values
    """
    headers = {}
    for line in headers_str.split('\n'):
        line = line.strip()
        if ':' in line:
            key, value = line.split(':', 1)
            headers[key.strip()] = value.strip()
    return headers

def dict_to_query_string(params: Dict[str, Any]) -> str:
    """
    Convert a dictionary to a URL-encoded query string.
    
    Args:
        params: Dictionary of parameters
        
    Returns:
        str: URL-encoded query string
    """
    return '&'.join([f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items()])

def parse_query_string(query: str) -> Dict[str, List[str]]:
    """
    Parse a URL query string into a dictionary.
    
    Args:
        query: The query string to parse
        
    Returns:
        Dict[str, List[str]]: Dictionary of parameter names and their values
    """
    return parse_qs(query)

def get_url_without_query(url: str) -> str:
    """
    Get the URL without query parameters and fragments.
    
    Args:
        url: The URL to process
        
    Returns:
        str: URL without query parameters and fragments
    """
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

def get_url_parameters(url: str) -> Dict[str, List[str]]:
    """
    Extract query parameters from a URL.
    
    Args:
        url: The URL to extract parameters from
        
    Returns:
        Dict[str, List[str]]: Dictionary of parameter names and their values
    """
    parsed = urlparse(url)
    return parse_qs(parsed.query)

def build_url(base_url: str, params: Dict[str, Any] = None) -> str:
    """
    Build a URL with query parameters.
    
    Args:
        base_url: The base URL
        params: Dictionary of query parameters
        
    Returns:
        str: The complete URL with query parameters
    """
    if not params:
        return base_url
    
    # Parse the base URL
    parsed = urlparse(base_url)
    
    # Parse existing query parameters
    query_params = parse_qs(parsed.query)
    
    # Update with new parameters
    for key, value in params.items():
        if key in query_params:
            if isinstance(query_params[key], list):
                query_params[key].append(str(value))
            else:
                query_params[key] = [query_params[key], str(value)]
        else:
            query_params[key] = [str(value)]
    
    # Rebuild the query string
    query_string = '&'.join(
        f"{k}={urllib.parse.quote(vv, safe='')}" 
        for k, vs in query_params.items() 
        for vv in vs
    )
    
    # Reconstruct the URL
    return parsed._replace(query=query_string).geturl()

def is_html_content(content_type: str) -> bool:
    """
    Check if the content type indicates HTML content.
    
    Args:
        content_type: The Content-Type header value
        
    Returns:
        bool: True if the content type is HTML, False otherwise
    """
    if not content_type:
        return False
    return 'text/html' in content_type.lower()

def is_json_content(content_type: str) -> bool:
    """
    Check if the content type indicates JSON content.
    
    Args:
        content_type: The Content-Type header value
        
    Returns:
        bool: True if the content type is JSON, False otherwise
    """
    if not content_type:
        return False
    return 'application/json' in content_type.lower()

def parse_json_safely(json_str: str) -> Optional[Union[Dict, List]]:
    """
    Safely parse a JSON string, returning None on failure.
    
    Args:
        json_str: The JSON string to parse
        
    Returns:
        Optional[Union[Dict, List]]: Parsed JSON data or None if parsing fails
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return None

def get_random_user_agent() -> str:
    """
    Get a random user agent string.
    
    Returns:
        str: A random user agent string
    """
    user_agents = [
        # Chrome
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
        # Firefox
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
        # Safari
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        # Edge
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
    ]
    return random.choice(user_agents)

# Example usage
if __name__ == "__main__":
    # Test URL functions
    test_url = "https://example.com/path?param1=value1&param2=value2#fragment"
    print(f"Original URL: {test_url}")
    print(f"Normalized URL: {normalize_url(test_url)}")
    print(f"Domain: {get_domain(test_url)}")
    print(f"URL without query: {get_url_without_query(test_url)}")
    print(f"URL parameters: {get_url_parameters(test_url)}")
    
    # Test random string generation
    print(f"Random string: {generate_random_string(10)}")
    
    # Test hashing
    test_str = "test123"
    print(f"MD5 of '{test_str}': {md5_hash(test_str)}")
    print(f"SHA-256 of '{test_str}': {sha256_hash(test_str)}")
    
    # Test IP validation
    print(f"Is '192.168.1.1' a valid IP? {is_ip_address('192.168.1.1')}")
    print(f"Is 'example.com' a valid IP? {is_ip_address('example.com')}")
    
    # Test random user agent
    print(f"Random user agent: {get_random_user_agent()}")
