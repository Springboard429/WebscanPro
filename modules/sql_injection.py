"""
SQL Injection Scanner Module for WebScanPro

This module tests for SQL injection vulnerabilities using various techniques
including error-based, boolean-based, and time-based SQL injection.
"""
import re
import requests
from typing import List, Dict, Any, Optional
import time
import random
import string
from urllib.parse import urljoin
import concurrent.futures
from modules.payload_manager import PayloadManager

from core.request_handler import RequestHandler
from core.response_analyzer import ResponseAnalyzer

class SQLInjectionScanner:
    """Scans for SQL injection vulnerabilities in web applications."""
    
    def __init__(self, request_handler: RequestHandler = None):
        """
        Initialize the SQLInjectionScanner.
        
        Args:
            request_handler: Optional request handler for making HTTP requests
        """
        self.request_handler = request_handler or RequestHandler()
        self.response_analyzer = ResponseAnalyzer()
        
        # Initialize payload manager
        self.payload_manager = PayloadManager()
        
        # Load payloads (base + API if available)
        self.payloads = self.payload_manager.get_all_payloads(use_api=True)
        
        print(f"[SQLi] Initialized with {len(self.payloads)} payloads")
    
    def scan_forms(self, forms: List[Dict], crawler: 'WebCrawler' = None) -> List[Dict[str, Any]]:
        """
        Scan forms for SQL injection vulnerabilities.
        
        Args:
            forms: List of form dictionaries from the crawler
            crawler: Optional authenticated crawler for re-authentication
            
        Returns:
            List of found vulnerabilities
        """
        vulnerabilities = []
        
        for form in forms:
            url = form.get('url', '')
            method = form.get('method', 'get').lower()
            inputs = form.get('inputs', [])
            
            # Use provided crawler or default request handler
            if crawler:
                # Get original response for comparison
                original_data = {inp['name']: inp.get('value', '') for inp in inputs}
                original_response = crawler.session.post(url, data=original_data) if method == 'post' else crawler.session.get(url, params=original_data)
                original_response.original_content = original_response.text
                
                for input_field in inputs:
                    input_name = input_field.get('name')
                    if not input_name:
                        continue
                        
                    for payload in self.payloads:
                        try:
                            print(f"[SQLi] Testing form input '{input_name}' with payload: '{payload}'")
                            test_data = {inp['name']: inp.get('value', '') for inp in inputs}
                            test_data[input_name] = payload
                            
                            if method == 'post':
                                test_response = crawler.session.post(url, data=test_data)
                            else:
                                test_response = crawler.session.get(url, params=test_data)
                            
                            # Check if redirected to login (session lost) - only re-auth if credentials exist
                            if 'login.php' in test_response.url and crawler.username and crawler.password:
                                print(f"[!] Session lost during SQL injection form test, re-authenticating...")
                                crawler._authenticate(crawler.username, crawler.password)
                                # Retry the request
                                if method == 'post':
                                    test_response = crawler.session.post(url, data=test_data)
                                else:
                                    test_response = crawler.session.get(url, params=test_data)
                            
                            test_response.original_content = original_response.text
                            
                            if self._is_vulnerable(test_response):
                                vuln = {
                                    'type': 'SQL Injection',
                                    'url': test_response.url,
                                    'parameter': input_name,
                                    'payload': payload,
                                    'method': method.upper(),
                                    'severity': 'High',
                                    'description': f'SQL injection vulnerability in {input_name} parameter',
                                    'recommendation': 'Use parameterized queries or prepared statements'
                                }
                                vulnerabilities.append(vuln)
                                print(f"[SQLi] ✅ FORM VULNERABILITY FOUND with payload: '{payload}' on input '{input_name}'")
                                break  # Found a vulnerability, move to next input
                        except Exception as e:
                            print(f"[!] Error testing form payload {payload}: {str(e)}")
                            continue
            else:
                # Use default request handler
                # Get original response for comparison
                original_data = {inp['name']: inp.get('value', '') for inp in inputs}
                original_response = self.request_handler.post(url, data=original_data) if method == 'post' else self.request_handler.get(url, params=original_data)
                original_response.original_content = original_response.text
                
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
                        
                        response.original_content = original_response.text
                        
                        if self._is_vulnerable(response):
                            vuln = {
                                'type': 'SQL Injection',
                                'url': response.url,
                                'parameter': input_name,
                                'payload': payload,
                                'method': method.upper(),
                                'severity': 'High',
                                'description': f'SQL injection vulnerability in {input_name} parameter',
                                'recommendation': 'Use parameterized queries or prepared statements'
                            }
                            vulnerabilities.append(vuln)
                            print(f"[SQLi] ✅ FORM VULNERABILITY FOUND with payload: '{payload}' on input '{input_name}'")
                            break  # Found a vulnerability, move to next input
        
        return vulnerabilities
    
    def scan_url_parameters_fast(self, url: str, params: Dict[str, str], crawler: 'WebCrawler' = None) -> List[Dict[str, Any]]:
        """
        Fast concurrent scan of URL parameters for SQL injection vulnerabilities.
        
        Args:
            url: The target URL
            params: Dictionary of parameters to test
            crawler: Optional authenticated crawler for re-authentication
            
        Returns:
            List of found vulnerabilities
        """
        vulnerabilities = []
        
        if not params:
            return vulnerabilities
            
        def test_parameter(param_name):
            """Test a single parameter with all payloads"""
            param_vulns = []
            for payload in self.payloads:
                try:
                    print(f"[SQLi] Testing parameter '{param_name}' with payload: '{payload}'")
                    if crawler:
                        test_response = crawler.session.get(url, params={param_name: payload})
                        # Check if redirected to login (session lost)
                        if 'login.php' in test_response.url and crawler.username and crawler.password:
                            crawler._authenticate(crawler.username, crawler.password)
                            test_response = crawler.session.get(url, params={param_name: payload})
                    else:
                        test_params = {param_name: payload}
                        test_response = self.request_handler.get(url, params=test_params)
                    
                    if self._is_vulnerable(test_response):
                        vuln = {
                            'type': 'SQL Injection',
                            'url': test_response.url,
                            'parameter': param_name,
                            'payload': payload,
                            'method': 'GET',
                            'severity': 'High',
                            'description': f'SQL injection vulnerability in {param_name} parameter',
                            'recommendation': 'Use parameterized queries or prepared statements'
                        }
                        param_vulns.append(vuln)
                        print(f"[SQLi] ✅ VULNERABILITY FOUND with payload: '{payload}'")
                        break  # Found vulnerability, stop testing this parameter
                except Exception as e:
                    print(f"[SQLi] ❌ Error testing payload '{payload}': {str(e)}")
                    continue
            return param_vulns
        
        # Use ThreadPoolExecutor for concurrent testing
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_to_param = {executor.submit(test_parameter, param_name): param_name 
                             for param_name in params.keys()}
            
            for future in concurrent.futures.as_completed(future_to_param):
                param_vulns = future.result()
                vulnerabilities.extend(param_vulns)
        
        return vulnerabilities
    
    def scan_url_parameters(self, url: str, params: Dict[str, str], crawler: 'WebCrawler' = None) -> List[Dict[str, Any]]:
        """
        Scan URL parameters for SQL injection vulnerabilities.
        
        Args:
            url: The target URL
            params: Dictionary of parameters to test
            crawler: Optional authenticated crawler for re-authentication
            
        Returns:
            List of found vulnerabilities
        """
        vulnerabilities = []
        
        # Use provided crawler or create new request handler
        if crawler:
            # Get original response for comparison
            original_response = crawler.session.get(url, params=params)
            original_response.original_content = original_response.text
            
            for param_name, param_value in params.items():
                for payload in self.payloads:
                    # Re-authenticate if needed (DVWA security)
                    try:
                        test_response = crawler.session.get(url, params={param_name: payload})
                        
                        # Check if redirected to login (session lost) - only re-auth if credentials exist
                        if 'login.php' in test_response.url and crawler.username and crawler.password:
                            print(f"[!] Session lost during SQL injection test, re-authenticating...")
                            # Re-authenticate
                            crawler._authenticate(crawler.username, crawler.password)
                            # Retry the request
                            test_response = crawler.session.get(url, params={param_name: payload})
                        
                        test_response.original_content = original_response.text
                        
                        if self._is_vulnerable(test_response):
                            vuln = {
                                'type': 'SQL Injection',
                                'url': test_response.url,
                                'parameter': param_name,
                                'payload': payload,
                                'method': 'GET',
                                'severity': 'High',
                                'description': f'SQL injection vulnerability in {param_name} parameter',
                                'recommendation': 'Use parameterized queries or prepared statements'
                            }
                            vulnerabilities.append(vuln)
                            break  # Found a vulnerability, move to next parameter
                    except Exception as e:
                        print(f"[!] Error testing payload {payload}: {str(e)}")
                        continue
        else:
            # Use default request handler
            # Get original response for comparison
            original_response = self.request_handler.get(url, params=params)
            original_response.original_content = original_response.text
            
            for param_name, param_value in params.items():
                for payload in self.payloads:
                    test_params = params.copy()
                    test_params[param_name] = payload
                    
                    response = self.request_handler.get(url, params=test_params)
                    response.original_content = original_response.text
                    
                    if self._is_vulnerable(response):
                        vuln = {
                            'type': 'SQL Injection',
                            'url': response.url,
                            'parameter': param_name,
                            'payload': payload,
                            'method': 'GET',
                            'severity': 'High',
                            'description': f'SQL injection vulnerability in {param_name} parameter',
                            'recommendation': 'Use parameterized queries or prepared statements'
                        }
                        vulnerabilities.append(vuln)
                        break  # Found a vulnerability, move to next parameter
        
        return vulnerabilities
    
    def _is_vulnerable(self, response) -> bool:
        """
        Check if a response indicates a SQL injection vulnerability.
        
        Args:
            response: requests.Response object
            
        Returns:
            bool: True if vulnerable
        """
        # Check for SQL error messages in response
        error_patterns = [
            r"SQL syntax.*MySQL",
            r"Warning.*mysql_.*",
            r"MySQLSyntaxErrorException",
            r"valid MySQL result",
            r"System.Data.SqlClient.SqlException",
            r"Microsoft SQL Native Client error.*",
            r"Unclosed quotation mark after the character string",
            r"ORA-\d{5}",
            r"Oracle error",
            r"Oracle.*Driver",
            r"PostgreSQL.*ERROR",
            r"Warning.*\\Wpg_.*",
            r"valid PostgreSQL result",
            r"SQLite/JDBCDriver",
            r"SQLite.Exception",
            r"SQL syntax.*",
            r"Warning.*sql_.*",
            r"quoted string not properly terminated",
        ]
        
        content = response.text
        
        # Check for SQL errors
        for pattern in error_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        # Additional check: Detect successful injection by content changes
        # This is useful for DVWA which doesn't show errors in low security mode
        if hasattr(response, 'original_content'):
            # Compare with original content
            content_length_diff = abs(len(content) - len(response.original_content))
            # If content length changed significantly, likely vulnerable
            if content_length_diff > 50:  # Threshold for content change
                return True
        else:
            # Store original content for comparison (this would be set by scanner)
            pass
            
        # Check for common injection success indicators
        success_indicators = [
            r"union select",
            r"order by.*\d+",
            r"and.*\d+=\d+",
            r"or.*\d+=\d+",
            r"sleep\(",
            r"benchmark\(",
            r"waitfor delay",
        ]
        
        for indicator in success_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                return True
        
        return False
