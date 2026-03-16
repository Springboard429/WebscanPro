"""
WebCrawler module for WebScanPro

This module provides functionality to crawl websites, discover pages,
and extract forms and input fields for security testing.
"""
import re
import time
from urllib.parse import urljoin, urlparse, urlunparse
from typing import List, Dict, Set, Optional, Tuple
import requests
from bs4 import BeautifulSoup, SoupStrainer
from bs4.element import Tag

from config import REQUEST_TIMEOUT, USER_AGENT, EXCLUDE_EXTENSIONS, MAX_DEPTH, MAX_PAGES

class WebCrawler:
    """Web crawler to discover pages and extract forms from a target website."""
    
    def __init__(self, base_url: str, username: str = None, password: str = None):
        """
        Initialize the WebCrawler.
        
        Args:
            base_url: The base URL to start crawling from
            username: Optional username for authentication
            password: Optional password for authentication
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.visited_urls = set()
        self.pages = []
        self.max_depth = MAX_DEPTH
        self.max_pages = MAX_PAGES
        self.request_timeout = REQUEST_TIMEOUT
        self.exclude_extensions = EXCLUDE_EXTENSIONS
        self.base_domain = self._get_domain(base_url)
        
        # Store credentials for re-authentication
        self.username = username
        self.password = password
        
        # Authenticate if credentials are provided
        if username and password:
            if not self._authenticate(username, password):
                print("Warning: Authentication failed")
        
        # Set user agent to look like a real browser
        self.session.headers.update({
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        })

    def _authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate with the target website (specifically for DVWA).
        
        Args:
            username: Username for authentication
            password: Password for authentication
            
        Returns:
            bool: True if authentication successful
        """
        try:
            # DVWA-specific login URL
            login_url = f"{self.base_domain}/login.php"
            
            print(f"Attempting to login to {login_url} with username: {username}")
            
            # First, get the login page to extract CSRF token
            response = self.session.get(login_url, timeout=self.request_timeout)
            
            if response.status_code != 200:
                print(f"[-] Failed to access login page. Status: {response.status_code}")
                return False
            
            # Extract CSRF token from the login form
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html')
            user_token = soup.find('input', {'name': 'user_token'})
            
            if not user_token:
                print("[-] Could not find CSRF token in login form")
                return False
            
            token_value = user_token.get('value', '')
            print(f"[+] Found CSRF token: {token_value}")
            
            # Prepare login data with CSRF token
            login_data = {
                'username': username,
                'password': password,
                'Login': 'Login',
                'user_token': token_value
            }
            
            # Perform login
            response = self.session.post(login_url, data=login_data, timeout=self.request_timeout)
            
            # Check if login was successful
            if response.status_code == 200:
                # Check multiple success indicators
                if 'index.php' in response.url:
                    print("[+] Authentication successful!")
                    return True
                elif 'login.php' in response.url:
                    # Check if we're actually logged in but redirected
                    if 'Login failed' not in response.text and 'logout' in response.text:
                        print("[+] Authentication successful (redirected to login with session)!")
                        return True
                    else:
                        print(f"[-] Authentication failed. Status: {response.status_code}")
                        print(f"Response URL: {response.url}")
                        # Show error details
                        if 'Login failed' in response.text:
                            print("   Error: Invalid credentials")
                        return False
                else:
                    print(f"[?] Unexpected response URL: {response.url}")
                    return False
            else:
                print(f"[-] Authentication failed. Status: {response.status_code}")
                print(f"Response URL: {response.url}")
                return False
                
        except Exception as e:
            print(f"[-] Authentication error: {str(e)}")
            return False

    def _get_domain(self, url: str) -> str:
        """Extract the domain from a URL."""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def _normalize_url(self, url: str) -> str:
        """Normalize URL by removing fragments but keeping query parameters."""
        parsed = urlparse(url)
        # Remove fragments but keep query parameters for vulnerability testing
        clean_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            '',  # params
            parsed.query,  # Keep query parameters!
            ''   # fragment
        )).rstrip('/')
        return clean_url

    def _is_same_domain(self, url: str) -> bool:
        """Check if URL belongs to the same domain."""
        return url.startswith(('http://', 'https://')) and self.base_domain in url

    def _should_skip(self, url: str) -> bool:
        """Check if URL should be skipped based on various conditions."""
        # Skip if already visited
        if url in self.visited_urls:
            return True
            
        # Skip if it's not a web page
        if any(url.lower().endswith(ext) for ext in self.exclude_extensions):
            return True
            
        # Skip if it's not the same domain
        if not self._is_same_domain(url):
            return True
            
        return False

    def _extract_url_params(self, url: str) -> Dict[str, str]:
        """Extract URL parameters from a URL."""
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        # Convert single-value lists to strings
        return {k: v[0] if v else '' for k, v in params.items()}

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> Set[str]:
        """Extract all links from a BeautifulSoup object."""
        links = set()
        
        # Find all anchor tags
        for tag in soup.find_all('a', href=True):
            url = urljoin(base_url, tag['href'])
            links.add(self._normalize_url(url))
            
        # Find all form actions
        for form in soup.find_all('form', action=True):
            url = urljoin(base_url, form['action'])
            links.add(self._normalize_url(url))
            
        return links

    def _extract_forms(self, soup: BeautifulSoup, url: str) -> List[Dict]:
        """Extract all forms from a page."""
        forms = []
        
        for form in soup.find_all('form'):
            form_data = {
                'action': urljoin(url, form.get('action', '')),
                'method': form.get('method', 'get').lower(),
                'inputs': [],
                'url': url
            }
            
            # Extract all input fields
            for input_tag in form.find_all(['input', 'textarea', 'select']):
                input_data = {
                    'type': input_tag.get('type', 'text'),
                    'name': input_tag.get('name'),
                    'value': input_tag.get('value', '')
                }
                
                # Handle select options
                if input_tag.name == 'select':
                    input_data['options'] = [
                        option.get('value', '') 
                        for option in input_tag.find_all('option')
                        if option.get('value')
                    ]
                    
                form_data['inputs'].append(input_data)
                
            forms.append(form_data)
            
        return forms

    def _get_page_content(self, url: str) -> Optional[Tuple[str, BeautifulSoup]]:
        """Fetch and parse a web page with retry logic."""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(
                    url,
                    timeout=self.request_timeout,
                    allow_redirects=True,
                    verify=False  # For testing only, should be configurable
                )
                
                # Only process successful HTML responses
                if response.status_code == 200 and 'text/html' in response.headers.get('content-type', '').lower():
                    return response.text, BeautifulSoup(response.text, 'lxml', parse_only=SoupStrainer(['a', 'form']))
                elif response.status_code == 200:
                    print(f"[!] Non-HTML content at {url}: {response.headers.get('content-type', 'unknown')}")
                else:
                    print(f"[!] HTTP {response.status_code} at {url}")
                    
            except requests.exceptions.Timeout:
                print(f"[!] Timeout fetching {url} (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
            except requests.exceptions.ConnectionError:
                print(f"[!] Connection error fetching {url} (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
            except (requests.RequestException, Exception) as e:
                print(f"[!] Error fetching {url}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
            
        return None

    def crawl(self, url: str = None, depth: int = 0) -> List[Dict]:
        """
        Crawl the website starting from the base URL.
        
        Args:
            url: Current URL to crawl
            depth: Current depth of the crawl
            
        Returns:
            List of pages with their forms and links
        """
        if len(self.pages) >= self.max_pages or depth > self.max_depth:
            return self.pages
            
        url = url or self.base_url
        original_url = url  # Keep original URL for parameter extraction
        url = self._normalize_url(url)
        
        # Skip if already visited or shouldn't be crawled
        if self._should_skip(url):
            return self.pages
            
        print(f"Crawling: {url} (Depth: {depth})")
        self.visited_urls.add(url)
        
        # Fetch and parse the page
        result = self._get_page_content(url)
        if not result:
            return self.pages
            
        content, soup = result
        
        # Extract forms and links
        forms = self._extract_forms(soup, url)
        links = self._extract_links(soup, url)
        
        # Extract URL parameters from the ORIGINAL URL (before normalization)
        params = self._extract_url_params(original_url)
        
        # Special handling for SQL injection pages - add test parameters
        if 'sqli' in url.lower() and not params:
            params = {
                'id': '1',
                'Submit': 'Submit'
            }
            print(f"[+] Added SQL injection test parameters to {url}")
        
        # Add page to results
        self.pages.append({
            'url': url,
            'forms': forms,
            'links': list(links),
            'params': params,
            'depth': depth
        })
        
        # Recursively crawl linked pages
        if depth < self.max_depth:  # Only recurse if we haven't reached max depth
            for link in links:
                if len(self.pages) >= self.max_pages:
                    break
                if link not in self.visited_urls:
                    self.crawl(link, depth + 1)
                
        return self.pages

    def get_sitemap(self) -> Dict[str, List[str]]:
        """Generate a sitemap of the crawled pages."""
        sitemap = {}
        for page in self.pages:
            sitemap[page['url']] = page['links']
        return sitemap

    def get_forms(self) -> List[Dict]:
        """Get all forms found during crawling."""
        forms = []
        for page in self.pages:
            for form in page['forms']:
                form['page_url'] = page['url']
                forms.append(form)
        return forms

    def close(self) -> None:
        """Close the session."""
        self.session.close()