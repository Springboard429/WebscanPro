"""
IDOR (Insecure Direct Object Reference) Tester Module for WebScanPro

This module specifically focuses on testing for IDOR vulnerabilities
by manipulating object references in requests.
"""
from typing import List, Dict, Any, Optional
import re
import random
import string
from urllib.parse import urljoin, parse_qs, urlparse

from core.request_handler import RequestHandler
from core.response_analyzer import ResponseAnalyzer

class IDORTester:
    """Tests for Insecure Direct Object Reference (IDOR) vulnerabilities."""
    
    def __init__(self, request_handler: RequestHandler):
        """
        Initialize the IDORTester.
        
        Args:
            request_handler: Instance of RequestHandler for making HTTP requests
        """
        self.request_handler = request_handler
        self.analyzer = ResponseAnalyzer()
        self.vulnerabilities: List[Dict[str, Any]] = []
    
    def test_url_parameters(self, url: str, params: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Test URL parameters for IDOR vulnerabilities.
        
        Args:
            url: The target URL
            params: Dictionary of parameters to test
            
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
    
    def test_json_payload(self, url: str, json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Test JSON payload for IDOR vulnerabilities.
        
        Args:
            url: The target URL
            json_data: Dictionary containing the JSON payload
            
        Returns:
            List of found vulnerabilities
        """
        vulnerabilities = []
        
        # Flatten the JSON and test each value
        flat_data = self._flatten_json(json_data)
        
        for key_path, value in flat_data.items():
            if not self._is_idor_candidate(key_path, str(value)):
                continue
                
            # Test with modified value
            if str(value).isdigit():
                test_value = str(int(value) + 1)
                test_data = self._update_json_value(json_data.copy(), key_path, test_value)
                
                response = self.request_handler.post(url, json=test_data)
                if self._is_idor_vulnerable(response, key_path, test_value):
                    vuln = {
                        'type': 'Insecure Direct Object Reference (IDOR)',
                        'url': url,
                        'parameter': key_path,
                        'original_value': value,
                        'tested_value': test_value,
                        'severity': 'High',
                        'description': f'IDOR vulnerability found in JSON field: {key_path}',
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
                (str(param_value).isdigit() or len(str(param_value)) > 5))
    
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
    
    def _flatten_json(self, json_data: Dict, parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """
        Flatten a nested JSON object.
        
        Args:
            json_data: The JSON object to flatten
            parent_key: Used for recursion
            sep: Separator between keys
            
        Returns:
            Flattened dictionary
        """
        items = {}
        for k, v in json_data.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.update(self._flatten_json(v, new_key, sep=sep))
            else:
                items[new_key] = v
        return items
    
    def _update_json_value(self, json_data: Dict, key_path: str, new_value: Any, sep: str = '.') -> Dict:
        """
        Update a value in a nested JSON object using a key path.
        
        Args:
            json_data: The JSON object to update
            key_path: Dot-separated path to the value to update
            new_value: New value to set
            sep: Separator between keys
            
        Returns:
            Updated JSON object
        """
        keys = key_path.split(sep)
        current = json_data
        for key in keys[:-1]:
            current = current.setdefault(key, {})
        current[keys[-1]] = new_value
        return json_data