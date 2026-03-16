"""
Response Analyzer for WebScanPro

This module analyzes HTTP responses for potential vulnerabilities.
"""
import re
from typing import Dict, List, Optional, Pattern, Union
from bs4 import BeautifulSoup

class ResponseAnalyzer:
    """Analyzes HTTP responses for potential vulnerabilities."""
    
    def __init__(self):
        """Initialize the ResponseAnalyzer."""
        self.error_patterns = {
            'sql': [
                # MySQL
                r"SQL syntax.*MySQL",
                r"Warning.*mysql_.*",
                r"MySQLSyntaxErrorException",
                r"valid MySQL result",
                # SQL Server
                r"System.Data.SqlClient.SqlException",
                r"Microsoft SQL Native Client error.*",
                r"Unclosed quotation mark after the character string",
                # Oracle
                r"ORA-\d{5}",
                r"Oracle error",
                r"Oracle.*Driver",
                # PostgreSQL
                r"PostgreSQL.*ERROR",
                r"Warning.*\\Wpg_.*",
                r"valid PostgreSQL result",
            ],
            'xss': [
                r"<script[^>]*>.*?</script>",
                r"<img[^>]*onerror=.*?>",
                r"<svg[^>]*onload=.*?>",
                r"on\\w+\\s*=\\s*[\"\\']?[^>]*[\"\\']?",
                r"javascript:[^\\s]*",
            ]
        }
    
    def contains_errors(self, response_text: str, error_type: str = 'sql') -> bool:
        """
        Check if the response contains error patterns.
        
        Args:
            response_text: The response text to analyze
            error_type: Type of errors to check for ('sql', 'xss', etc.)
            
        Returns:
            bool: True if errors are found, False otherwise
        """
        patterns = self.error_patterns.get(error_type.lower(), [])
        for pattern in patterns:
            if re.search(pattern, response_text, re.IGNORECASE | re.DOTALL):
                return True
        return False
    
    def is_redirect(self, response) -> bool:
        """
        Check if the response is a redirect.
        
        Args:
            response: requests.Response object
            
        Returns:
            bool: True if the response is a redirect
        """
        return response.is_redirect or response.status_code in (301, 302, 303, 307, 308)
    
    def get_forms(self, response_text: str, base_url: str = None) -> List[Dict]:
        """
        Extract forms from HTML content.
        
        Args:
            response_text: HTML content
            base_url: Base URL for resolving relative form actions
            
        Returns:
            List of form details
        """
        forms = []
        soup = BeautifulSoup(response_text, 'lxml')
        
        for form in soup.find_all('form'):
            form_details = {
                'action': self._resolve_url(form.get('action', ''), base_url),
                'method': form.get('method', 'get').lower(),
                'inputs': [],
                'url': base_url
            }
            
            # Get all input fields
            for tag in form.find_all(['input', 'textarea', 'select']):
                input_details = {
                    'type': tag.get('type', 'text'),
                    'name': tag.get('name'),
                    'value': tag.get('value', '')
                }
                form_details['inputs'].append(input_details)
            
            forms.append(form_details)
        
        return forms
    
    def _resolve_url(self, url: str, base_url: str = None) -> str:
        """
        Resolve a relative URL against a base URL.
        
        Args:
            url: URL to resolve
            base_url: Base URL
            
        Returns:
            Resolved URL
        """
        if not url or not base_url:
            return url
            
        if url.startswith(('http://', 'https://')):
            return url
            
        return f"{base_url.rstrip('/')}/{url.lstrip('/')}"
    
    def find_links(self, response_text: str, base_url: str = None) -> List[str]:
        """
        Extract links from HTML content.
        
        Args:
            response_text: HTML content
            base_url: Base URL for resolving relative links
            
        Returns:
            List of absolute URLs
        """
        links = set()
        soup = BeautifulSoup(response_text, 'lxml')
        
        for tag in soup.find_all(['a', 'link', 'script', 'img'], href=True):
            url = self._resolve_url(tag['href'], base_url)
            if url:
                links.add(url)
                
        for tag in soup.find_all(['img', 'script'], src=True):
            url = self._resolve_url(tag['src'], base_url)
            if url:
                links.add(url)
                
        return list(links)
    
    def detect_technologies(self, response) -> Dict[str, List[str]]:
        """
        Detect technologies used by the web application.
        
        Args:
            response: requests.Response object
            
        Returns:
            Dictionary of technology categories and detected technologies
        """
        tech = {
            'server': self._detect_server_tech(response),
            'framework': self._detect_framework(response),
            'languages': self._detect_languages(response),
            'javascript': self._detect_javascript_libs(response),
            'analytics': self._detect_analytics(response),
            'cms': self._detect_cms(response)
        }
        
        return {k: v for k, v in tech.items() if v}
    
    def _detect_server_tech(self, response) -> List[str]:
        """Detect server technologies from response headers."""
        servers = []
        server = response.headers.get('Server')
        if server:
            servers.append(server)
        powered_by = response.headers.get('X-Powered-By')
        if powered_by:
            servers.append(powered_by)
        return servers
    
    def _detect_framework(self, response) -> List[str]:
        """Detect web frameworks from response."""
        frameworks = []
        # Add framework detection logic here
        return frameworks
    
    def _detect_languages(self, response) -> List[str]:
        """Detect programming languages from response."""
        languages = []
        # Add language detection logic here
        return languages
    
    def _detect_javascript_libs(self, response) -> List[str]:
        """Detect JavaScript libraries from response."""
        libs = []
        # Add JS library detection logic here
        return libs
    
    def _detect_analytics(self, response) -> List[str]:
        """Detect analytics services from response."""
        analytics = []
        # Add analytics detection logic here
        return analytics
    
    def _detect_cms(self, response) -> List[str]:
        """Detect content management systems from response."""
        cms = []
        # Add CMS detection logic here
        return cms