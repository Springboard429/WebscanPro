"""
XSS (Cross-Site Scripting) Scanner Module for WebScanPro

This module tests for various types of XSS vulnerabilities including
reflected, stored, and DOM-based XSS.
"""
from typing import List, Dict, Any, Optional
import re
import random
import string
from urllib.parse import urljoin, quote_plus

from core.request_handler import RequestHandler
from core.response_analyzer import ResponseAnalyzer

class XSSScanner:
    """Scans for Cross-Site Scripting (XSS) vulnerabilities in web applications."""
    
    def __init__(self, request_handler: RequestHandler = None):
        """
        Initialize the XSSScanner.
        
        Args:
            request_handler: Optional RequestHandler instance
        """
        self.request_handler = request_handler or RequestHandler()
        self.analyzer = ResponseAnalyzer()
        self.vulnerabilities: List[Dict[str, Any]] = []
        
        # XSS payloads to test - reduced for faster scanning
        self.payloads = [
            # Basic XSS - most effective payloads first
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "\" onmouseover=alert('XSS')",
            "' onmouseover=alert('XSS')",
            "javascript:alert('XSS')",
        ]
    
    def scan_forms(self, forms: List[Dict]) -> List[Dict[str, Any]]:
        """
        Scan forms for XSS vulnerabilities.
        
        Args:
            forms: List of form dictionaries from the crawler
            
        Returns:
            List of found vulnerabilities
        """
        vulnerabilities = []
        
        for form in forms:
            url = form.get('url', '')
            method = form.get('method', 'get').lower()
            inputs = form.get('inputs', [])
            
            for input_field in inputs:
                input_name = input_field.get('name')
                if not input_name:
                    continue
                    
                for payload in self.payloads:
                    test_data = {inp['name']: inp.get('value', '') for inp in inputs}
                    test_data[input_name] = payload
                    
                    if method == 'post':
                        response = self.request_handler.post(url, data=test_data)
                    else:
                        response = self.request_handler.get(url, params=test_data)
                    
                    if self._is_vulnerable(response, payload):
                        vuln = {
                            'type': 'Cross-Site Scripting (XSS)',
                            'url': response.url,
                            'parameter': input_name,
                            'payload': payload,
                            'method': method.upper(),
                            'severity': 'High',
                            'description': f'XSS vulnerability in {input_name} parameter',
                            'recommendation': 'Implement proper input validation and output encoding'
                        }
                        vulnerabilities.append(vuln)
                        break  # Found a vulnerability, move to next input
        
        return vulnerabilities
    
    def scan_url_parameters(self, url: str, params: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Scan URL parameters for XSS vulnerabilities.
        
        Args:
            url: The target URL
            params: Dictionary of parameters to test
            
        Returns:
            List of found vulnerabilities
        """
        vulnerabilities = []
        
        for param_name, param_value in params.items():
            for payload in self.payloads:
                test_params = params.copy()
                test_params[param_name] = payload
                
                response = self.request_handler.get(url, params=test_params)
                
                if self._is_vulnerable(response, payload):
                    vuln = {
                        'type': 'Cross-Site Scripting (XSS)',
                        'url': response.url,
                        'parameter': param_name,
                        'payload': payload,
                        'method': 'GET',
                        'severity': 'High',
                        'description': f'XSS vulnerability in {param_name} parameter',
                        'recommendation': 'Implement proper input validation and output encoding'
                    }
                    vulnerabilities.append(vuln)
                    break  # Found a vulnerability, move to next parameter
        
        return vulnerabilities
    
    def _is_vulnerable(self, response, payload: str) -> bool:
        """
        Check if a response indicates an XSS vulnerability.
        
        Args:
            response: requests.Response object
            payload: The XSS payload that was sent
            
        Returns:
            bool: True if vulnerable
        """
        # Check if the payload is reflected in the response
        if payload in response.text:
            return True
            
        # Check for common XSS patterns in the response
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"<img[^>]*onerror=.*?>",
            r"<svg[^>]*onload=.*?>",
            r"on\\w+\\s*=\\s*[\"\\']?[^>]*[\"\\']?",
            r"javascript:[^\\s]*",
        ]
        
        content = response.text
        return any(re.search(pattern, content, re.IGNORECASE | re.DOTALL) for pattern in xss_patterns)