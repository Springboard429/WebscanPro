"""WebScanPro - Access Control & IDOR Testing Module"""

import requests
import json
import sys
from urllib.parse import urljoin

def login_dvwa(base_url, login_url, username="admin", password="password"):
    """Authenticates with DVWA and forces the security level to Low."""
    session = requests.Session()
    try:
        login_page = session.get(login_url)
        # Extract CSRF token
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(login_page.text, 'html.parser')
        user_token = soup.find('input', {'name': 'user_token'})
        user_token_value = user_token['value'] if user_token else None

        login_data = {'username': username, 'password': password, 'Login': 'Login'}
        if user_token_value:
            login_data['user_token'] = user_token_value

        response = session.post(login_url, data=login_data)
        if response.status_code == 200 and "login.php" not in response.url:
            print("[+] Login successful for IDOR testing.")
            session.cookies.set('security', 'low')
            return session
        else:
            print("[-] Login failed.")
            return None
    except Exception as e:
        print(f"[-] Login error: {e}")
        return None

def test_broken_access_control(url):
    """
    Tests if a protected URL can be accessed without authentication.
    """
    # Create a brand new session with NO cookies
    unauth_session = requests.Session()
    
    try:
        response = unauth_session.get(url, allow_redirects=True)
        
        # In a secure app, unauthenticated users should be redirected to a login page
        # If we get a 200 OK and we are NOT on the login page, it's vulnerable!
        if response.status_code == 200 and 'login.php' not in response.url:
            return {
                'url': url,
                'vulnerability_type': 'Broken Access Control',
                'description': 'Page is accessible without authentication.',
                'remediation': 'Implement proper session validation on all restricted endpoints before rendering content.'
            }
    except requests.RequestException as e:
        print(f"[-] Error connecting to {url}: {e}")
        
    return None

def test_idor(url, form, session):
    """
    Tests for IDOR by enumerating numeric ID parameters.
    """
    vulnerabilities = []
    action = urljoin(url, form['action']) if form['action'] else url
    method = form.get('method', 'get').lower()
    
    # Common parameter names that indicate IDOR targets
    idor_targets = ['id', 'user_id', 'uid', 'account_id', 'profile']
    
    for input_field in form['inputs']:
        name = input_field['name']
        if name.lower() in idor_targets:
            print(f"    [*] IDOR target parameter found: '{name}'. Enumerating values 1-3...")
            
            responses = []
            # Try accessing user IDs 1, 2, and 3
            for test_id in ['1', '2', '3']:
                data = {}
                for inp in form['inputs']:
                    data[inp['name']] = inp.get('value', '') if inp['name'] != name else test_id
                
                if method == 'post':
                    res = session.post(action, data=data)
                else:
                    res = session.get(action, params=data)
                
                # Store the length of the response
                responses.append(len(res.text))
            
            # Logic: If ID 1, 2, and 3 all return drastically different response lengths, 
            # it means we are successfully pulling different users' data profiles!
            if len(set(responses)) > 1:
                print(f"  [!] IDOR Found: Parameter '{name}' allows unauthorized data enumeration.")
                vulnerabilities.append({
                    'url': action,
                    'vulnerability_type': 'Insecure Direct Object Reference (IDOR)',
                    'vulnerable_input': name,
                    'description': f'Manipulating the {name} parameter returned unique data records.',
                    'remediation': 'Implement access control checks to verify the authenticated user is authorized to access the requested object ID.'
                })
                
    return vulnerabilities

def main():
    if len(sys.argv) < 3:
        print("Usage: python access_control_tester.py <base_url> <login_url> [crawler_output]")
        print("Example: python access_control_tester.py http://localhost http://localhost/login.php result.json")
        sys.exit(1)
        
    base_url = sys.argv[1]
    login_url = sys.argv[2]
    crawler_output = sys.argv[3] if len(sys.argv) > 3 else 'result.json'
    
    try:
        with open(crawler_output, 'r') as f:
            crawler_data = json.load(f)
    except FileNotFoundError:
        print(f"[-] Crawler output file '{crawler_output}' not found. Run the crawler first.")
        sys.exit(1)

    print("\n[+] Starting Access Control & IDOR Tests...")
    all_vulnerabilities = []
    
    # We need an authenticated session for the IDOR tests
    auth_session = login_dvwa(base_url, login_url)
    if not auth_session:
        sys.exit(1)

    # Extract data from crawler output
    urls = [u.get('url', '') for u in crawler_data.get('urls', [])]
    forms = crawler_data.get('forms', [])

    # 1. Test Broken Access Control on all discovered URLs
    print("\n[*] Phase 1: Testing Broken Access Control (Unauthenticated Browsing)...")
    for url in urls:
        if 'vulnerabilities' in url:
            bac_vuln = test_broken_access_control(url)
            if bac_vuln:
                print(f"  [!] Broken Access Control Found: {url}")
                all_vulnerabilities.append(bac_vuln)

    # 2. Test IDOR on all discovered forms
    print("\n[*] Phase 2: Testing IDOR (Parameter Manipulation)...")
    for idx, form in enumerate(forms, 1):
        action = form.get('action', '')
        if not action:
            continue
            
        if 'vulnerabilities' in action:
            print(f"\n[*] Testing form {idx}: {action}")
            idor_vulns = test_idor(action, form, auth_session)
            all_vulnerabilities.extend(idor_vulns)

    # Save Results
    with open('modules/access_control_vulnerabilities.json', 'w') as f:
        json.dump(all_vulnerabilities, f, indent=4)
        
    print(f"\n[+] Testing complete. Found {len(all_vulnerabilities)} vulnerabilities.")
    print("[+] Results saved to modules/access_control_vulnerabilities.json")

if __name__ == "__main__":
    main()