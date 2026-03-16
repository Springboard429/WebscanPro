"""
Request Handler for WebScanPro

This module handles all HTTP requests made by the scanner.
"""
import requests
import time
from typing import Dict, Any, Optional
from urllib.parse import urljoin, urlparse

from config import REQUEST_TIMEOUT, USER_AGENT, MAX_REDIRECTS

class RequestHandler:
    """Handles HTTP requests with retries and error handling."""
    
    def __init__(self, base_url: str = None, session: requests.Session = None):
        """
        Initialize the RequestHandler.
        
        Args:
            base_url: Base URL for relative requests
            session: Optional requests.Session to reuse
        """
        self.base_url = base_url
        self.session = session or requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.session.max_redirects = MAX_REDIRECTS
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """
        Send a GET request.
        
        Args:
            url: URL to request
            **kwargs: Additional arguments for requests.get()
            
        Returns:
            Response object
        """
        url = self._prepare_url(url)
        return self._request('GET', url, **kwargs)
    
    def post(self, url: str, data: Dict = None, **kwargs) -> requests.Response:
        """
        Send a POST request.
        
        Args:
            url: URL to request
            data: Data to send in the request body
            **kwargs: Additional arguments for requests.post()
            
        Returns:
            Response object
        """
        url = self._prepare_url(url)
        return self._request('POST', url, data=data, **kwargs)
    
    def _prepare_url(self, url: str) -> str:
        """
        Prepare URL for the request.
        
        Args:
            url: URL to prepare
            
        Returns:
            Prepared URL
        """
        if not url.startswith(('http://', 'https://')) and self.base_url:
            return urljoin(self.base_url, url)
        return url
    
    def _request(self, method: str, url: str, max_retries: int = 3, **kwargs) -> requests.Response:
        """
        Send an HTTP request with retries.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: URL to request
            max_retries: Maximum number of retry attempts
            **kwargs: Additional arguments for requests.request()
            
        Returns:
            Response object
            
        Raises:
            requests.RequestException: If the request fails after all retries
        """
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                response = self.session.request(
                    method,
                    url,
                    timeout=REQUEST_TIMEOUT,
                    allow_redirects=True,
                    **kwargs
                )
                return response
                
            except requests.RequestException as e:
                last_exception = e
                if attempt == max_retries - 1:
                    raise
                
                # Exponential backoff
                time.sleep(2 ** attempt)
        
        raise last_exception or requests.RequestException("Unknown error occurred")
    
    def close(self) -> None:
        """Close the session."""
        self.session.close()