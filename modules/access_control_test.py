"""
Access Control Tester Module for WebScanPro

This module tests for various access control vulnerabilities including:
- Insecure Direct Object References (IDOR)
- Missing Function Level Access Control (MFLAC)
- Privilege Escalation
- Horizontal/Vertical Access Control Issues
"""
from typing import List, Dict, Any, Optional
import re
import random
import string
from urllib.parse import urljoin

from core.request_handler import RequestHandler
from core.response_analyzer import ResponseAnalyzer

class AccessControlTester:
    """Tests for access control vulnerabilities in web applications."""
    
    def __init__(self, request_handler: RequestHandler):
        """
        Initialize the AccessControlTester.
        
        Args:
            request_handler: Instance of RequestHandler for making HTTP requests
        """
        self.request_handler = request_handler
        self.analyzer = ResponseAnalyzer()
        self.vulnerabilities: List[Dict[str, Any]] = []
    
    def test_idor(self, url: str, params: Dict[str, str], user_context: Dict = None) -> List[Dict[str, Any]]:
        """
        Test for Insecure Direct Object References (IDOR) vulnerabilities.
        
        Args:
            url: The target URL
            params: Dictionary of parameters to test
            user_context: Optional user context for testing with authentication
            
        Returns:
            List of found vulnerabilities
        """
        vulnerabilities = []
        
        for param_name, param_value in params.items():
            if not self._is_idor_candidate(param_name, param_value):
                continue
                
            # Test with incremented value
            if param_value.isdigit():
                test_value = str(int(param_value) + 1)
                test_params = params.copy()
                test_params[param_name] = test_value
                
                response = self.request_handler.get(url, params=test_params)
                if self._is_idor_vulnerable(response, param_name, test_value):
                    vuln = {
                        'type': 'Insecure Direct Object Reference (IDOR)',
                        'url': response.url,
                        'parameter': param_name,
                        'original_value': param_value,
                        'tested_value': test_value,
                        'severity': 'High',
                        'description': f'IDOR vulnerability found in parameter: {param_name}',
                        'recommendation': 'Implement proper access control checks for all object references'
                    }
                    vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _is_idor_candidate(self, param_name: str, param_value: str) -> bool:
        """
        Check if a parameter is a potential IDOR candidate.
        
        Args:
            param_name: Name of the parameter
            param_value: Value of the parameter
            
        Returns:
            bool: True if the parameter is a candidate for IDOR testing
        """
        idor_keywords = ['id', 'user', 'account', 'order', 'invoice', 'document', 'file']
        return (any(keyword in param_name.lower() for keyword in idor_keywords) and
                (param_value.isdigit() or len(param_value) > 5))
    
    def _is_idor_vulnerable(self, response, param_name: str, test_value: str) -> bool:
        """
        Check if a response indicates an IDOR vulnerability.
        
        Args:
            response: requests.Response object
            param_name: Name of the tested parameter
            test_value: Value used for testing
            
        Returns:
            bool: True if vulnerable
        """
        if response.status_code == 200:
            # Check if the response contains the test value
            if str(test_value) in response.text:
                return True
                
            # Check for common error messages
            error_patterns = [
                r'not authorized',
                r'access denied',
                r'permission denied',
                r'unauthorized',
                r'forbidden',
                r'not found'
            ]
            
            content = response.text.lower()
            if any(re.search(pattern, content) for pattern in error_patterns):
                return False
                
            return True
            
        return False
    
    def test_privilege_escalation(self, endpoints: List[Dict], user_roles: List[str]) -> List[Dict[str, Any]]:
        """
        Test for privilege escalation vulnerabilities.
        
        Args:
            endpoints: List of endpoint dictionaries with 'url', 'method', and 'required_role'
            user_roles: List of roles the test user has
            
        Returns:
            List of found vulnerabilities
        """
        vulnerabilities = []
        
        for endpoint in endpoints:
            if not self._should_test_endpoint(endpoint, user_roles):
                continue
                
            method = endpoint.get('method', 'GET').upper()
            url = endpoint['url']
            
            if method == 'GET':
                response = self.request_handler.get(url)
            elif method == 'POST':
                response = self.request_handler.post(url, data=endpoint.get('data', {}))
            else:
                continue
                
            if self._is_privilege_escalation(response, endpoint, user_roles):
                vuln = {
                    'type': 'Privilege Escalation',
                    'url': url,
                    'method': method,
                    'required_role': endpoint.get('required_role', 'unknown'),
                    'user_roles': user_roles,
                    'severity': 'High',
                    'description': f'Privilege escalation possible to {endpoint.get("required_role")} endpoint',
                    'recommendation': 'Implement proper role-based access control'
                }
                vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _should_test_endpoint(self, endpoint: Dict, user_roles: List[str]) -> bool:
        """
        Determine if an endpoint should be tested based on user roles.
        
        Args:
            endpoint: Endpoint dictionary
            user_roles: List of user roles
            
        Returns:
            bool: True if the endpoint should be tested
        """
        required_role = endpoint.get('required_role')
        if not required_role:
            return False
            
        return required_role not in user_roles
    
    def _is_privilege_escalation(self, response, endpoint: Dict, user_roles: List[str]) -> bool:
        """
        Check if a response indicates a privilege escalation.
        
        Args:
            response: requests.Response object
            endpoint: Endpoint dictionary
            user_roles: List of user roles
            
        Returns:
            bool: True if privilege escalation is possible
        """
        if response.status_code == 200:
            # Check for access denied messages in successful responses
            denied_patterns = [
                r'access denied',
                r'not authorized',
                r'permission denied',
                r'unauthorized',
                r'forbidden'
            ]
            
            content = response.text.lower()
            if any(re.search(pattern, content) for pattern in denied_patterns):
                return False
                
            return True
                
        return False
    
    def test_missing_function_level_access_control(self, endpoints: List[Dict]) -> List[Dict[str, Any]]:
        """
        Test for Missing Function Level Access Control (MFLAC) vulnerabilities.
        
        Args:
            endpoints: List of endpoint dictionaries with 'url', 'method', and 'description'
            
        Returns:
            List of found vulnerabilities
        """
        vulnerabilities = []
        
        for endpoint in endpoints:
            method = endpoint.get('method', 'GET').upper()
            url = endpoint['url']
            
            if method == 'GET':
                response = self.request_handler.get(url)
            elif method == 'POST':
                response = self.request_handler.post(url, data=endpoint.get('data', {}))
            else:
                continue
                
            if self._is_mflac_vulnerable(response):
                vuln = {
                    'type': 'Missing Function Level Access Control',
                    'url': url,
                    'method': method,
                    'severity': 'High',
                    'description': endpoint.get('description', 'Missing function level access control'),
                    'recommendation': 'Implement proper access control checks for all functions'
                }
                vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _is_mflac_vulnerable(self, response) -> bool:
        """
        Check if a response indicates a Missing Function Level Access Control vulnerability.
        
        Args:
            response: requests.Response object
            
        Returns:
            bool: True if vulnerable
        """
        if response.status_code == 200:
            # Check for access denied messages in successful responses
            denied_patterns = [
                r'access denied',
                r'not authorized',
                r'permission denied',
                r'unauthorized',
                r'forbidden'
            ]
            
            content = response.text.lower()
            if any(re.search(pattern, content) for pattern in denied_patterns):
                return False
                
            return True
                
        return False