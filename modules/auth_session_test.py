"""
Authentication and Session Testing Module for WebScanPro

This module tests for various authentication and session management vulnerabilities including:
- Weak passwords
- Session fixation
- Session timeout
- Password policy
- Account lockout
- Brute force protection
"""
import time
import random
import string
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urljoin

from core.request_handler import RequestHandler
from core.response_analyzer import ResponseAnalyzer

class AuthSessionTester:
    """Tests for authentication and session management vulnerabilities."""
    
    def __init__(self, request_handler: RequestHandler):
        """
        Initialize the AuthSessionTester.
        
        Args:
            request_handler: Instance of RequestHandler for making HTTP requests
        """
        self.request_handler = request_handler
        self.analyzer = ResponseAnalyzer()
        self.vulnerabilities: List[Dict[str, Any]] = []
        self.session = request_handler.session
    
    def test_weak_credentials(self, login_url: str, username_param: str, 
                            password_param: str, users: List[Dict]) -> List[Dict[str, Any]]:
        """
        Test for weak or default credentials.
        
        Args:
            login_url: URL of the login page
            username_param: Name of the username parameter
            password_param: Name of the password parameter
            users: List of user dictionaries with 'username' and 'password'
            
        Returns:
            List of found vulnerabilities
        """
        vulnerabilities = []
        
        for user in users:
            data = {
                username_param: user['username'],
                password_param: user['password']
            }
            
            response = self.request_handler.post(login_url, data=data)
            
            if self._is_successful_login(response):
                vuln = {
                    'type': 'Weak Credentials',
                    'url': login_url,
                    'username': user['username'],
                    'password': user['password'],
                    'severity': 'High',
                    'description': f'Weak or default credentials found: {user["username"]}/{user["password"]}',
                    'recommendation': 'Enforce strong password policy and change default credentials'
                }
                vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def test_brute_force(self, login_url: str, username_param: str, 
                        password_param: str, username: str, 
                        max_attempts: int = 5) -> Dict[str, Any]:
        """
        Test for brute force attack protection.
        
        Args:
            login_url: URL of the login page
            username_param: Name of the username parameter
            password_param: Name of the password parameter
            username: Username to test with
            max_attempts: Number of failed attempts to try
            
        Returns:
            Dictionary with test results
        """
        results = {
            'vulnerable': False,
            'attempts': 0,
            'locked': False,
            'status_codes': [],
            'response_times': []
        }
        
        for i in range(max_attempts):
            # Generate a random password
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            
            data = {
                username_param: username,
                password_param: password
            }
            
            start_time = time.time()
            response = self.request_handler.post(login_url, data=data)
            end_time = time.time()
            
            results['attempts'] += 1
            results['status_codes'].append(response.status_code)
            results['response_times'].append(end_time - start_time)
            
            # Check if account is locked
            if self._is_account_locked(response):
                results['locked'] = True
                break
                
            # Check if there's rate limiting
            if response.status_code == 429:  # Too Many Requests
                results['rate_limited'] = True
                break
        
        # If we made all attempts without being blocked or locked, it's vulnerable
        if not results['locked'] and not results.get('rate_limited', False):
            results['vulnerable'] = True
            self.vulnerabilities.append({
                'type': 'Brute Force Vulnerability',
                'url': login_url,
                'severity': 'High',
                'description': 'No protection against brute force attacks detected',
                'recommendation': 'Implement account lockout and rate limiting'
            })
        
        return results
    
    def test_session_fixation(self, login_url: str, username: str, password: str, 
                             session_param: str = 'sessionid') -> bool:
        """
        Test for session fixation vulnerability.
        
        Args:
            login_url: URL of the login page
            username: Valid username
            password: Valid password
            session_param: Name of the session cookie
            
        Returns:
            bool: True if vulnerable to session fixation
        """
        # Get a session cookie before login
        self.request_handler.get(login_url)
        session_cookie = self.session.cookies.get(session_param)
        
        if not session_cookie:
            return False
            
        # Login with the existing session
        data = {
            'username': username,
            'password': password
        }
        response = self.request_handler.post(login_url, data=data)
        
        # Check if the session ID remained the same
        new_session_cookie = self.session.cookies.get(session_param)
        if new_session_cookie == session_cookie:
            self.vulnerabilities.append({
                'type': 'Session Fixation',
                'url': login_url,
                'severity': 'High',
                'description': 'Session ID remains the same after login',
                'recommendation': 'Generate a new session ID after successful authentication'
            })
            return True
            
        return False
    
    def test_session_timeout(self, protected_url: str, login_url: str, 
                           username: str, password: str, 
                           timeout: int = 1800) -> bool:
        """
        Test session timeout.
        
        Args:
            protected_url: URL that requires authentication
            login_url: URL of the login page
            username: Valid username
            password: Valid password
            timeout: Expected session timeout in seconds
            
        Returns:
            bool: True if session timeout is not properly enforced
        """
        # Login
        data = {
            'username': username,
            'password': password
        }
        self.request_handler.post(login_url, data=data)
        
        # Access protected page
        response = self.request_handler.get(protected_url)
        if response.status_code != 200:
            return False
            
        # Wait for session to expire
        time.sleep(timeout + 1)
        
        # Try to access protected page again
        response = self.request_handler.get(protected_url)
        
        # If we can still access it, session timeout is not enforced
        if response.status_code == 200:
            self.vulnerabilities.append({
                'type': 'Insecure Session Timeout',
                'url': protected_url,
                'severity': 'Medium',
                'description': 'Session does not expire after the specified timeout',
                'recommendation': f'Enforce session timeout of {timeout} seconds'
            })
            return True
            
        return False
    
    def _is_successful_login(self, response) -> bool:
        """
        Check if a login attempt was successful.
        
        Args:
            response: requests.Response object from login attempt
            
        Returns:
            bool: True if login was successful
        """
        # Check for common indicators of successful login
        success_indicators = [
            'logout',
            'sign out',
            'welcome',
            'dashboard',
            'my account'
        ]
        
        content = response.text.lower()
        return any(indicator in content for indicator in success_indicators)
    
    def _is_account_locked(self, response) -> bool:
        """
        Check if an account is locked based on the response.
        
        Args:
            response: requests.Response object from login attempt
            
        Returns:
            bool: True if account appears to be locked
        """
        lock_indicators = [
            'account locked',
            'too many attempts',
            'temporarily locked',
            'suspended'
        ]
        
        content = response.text.lower()
        return any(indicator in content for indicator in lock_indicators)