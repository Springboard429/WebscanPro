"""WebScanPro - AI-Driven Cross-Site Scripting (XSS) Testing Module"""

import os
import sys
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from openai import OpenAI
import dotenv

dotenv.load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3-coder-next:cloud")

client = OpenAI(
    base_url=OLLAMA_BASE_URL,
    api_key="ollama"  
)

print(f"[*] Using Ollama model: {OLLAMA_MODEL} at {OLLAMA_BASE_URL}") 

def generate_llm_xss_payloads(form_data):
    """
    Passes the form structure to the LLM and requests tailored XSS payloads.
    """
    prompt = f"""
    You are an expert penetration tester. Analyze the following HTML form structure and generate 5 highly effective Cross-Site Scripting (XSS) payloads tailored for it.
    Form details: {json.dumps(form_data)}
    
    Requirements:
    - Include a mix of standard script tags, attribute breakouts (e.g., "><img src=x onerror=alert(1)>"), and event handler injections.
    - Use a unique identifier in the alert/console log like 'WebScanPro_XSS' so we can verify execution.
    - Respond ONLY with a valid JSON array of strings. 
    - Do not include markdown blocks, explanations, or any other text.
    
    Example format:
    ["<script>alert('WebScanPro_XSS')</script>", "\\"><svg/onload=alert('WebScanPro_XSS')>"]
    """
    
    try:
        response = client.chat.completions.create(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        text = response.choices[0].message.content.strip()
        
        # Clean up any accidental markdown formatting from the LLM
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        payloads = json.loads(text.strip())
        
        if isinstance(payloads, list) and len(payloads) > 0:
            return payloads
        else:
            raise ValueError("LLM did not return a valid list.")
            
    except Exception as e:
        print(f"[-] LLM Payload Generation failed: {e}. Falling back to default payloads.")
        return [
            "<script>alert('WebScanPro_XSS')</script>", 
            "\"><img src=x onerror=alert('WebScanPro_XSS')>",
            "qwerty<script>alert(1)</script>uiop"
        ]

def login_dvwa(base_url, login_url, username="admin", password="password"):
    session = requests.Session()
    try:
        login_page = session.get(login_url)
        soup = BeautifulSoup(login_page.text, 'html.parser')
        user_token = soup.find('input', {'name': 'user_token'})
        user_token_value = user_token['value'] if user_token else None

        login_data = {
            'username': username,
            'password': password,
            'Login': 'Login'
        }
        if user_token_value:
            login_data['user_token'] = user_token_value

        response = session.post(login_url, data=login_data)
        
        if response.status_code == 200:
            print("[+] Login successful.")
            
            session.cookies.set('security', 'low')
            print("[+] Security level forced to: low")
            
            return session
        else:
            print("[-] Login failed.")
            return None
    except Exception as e:
        print(f"[-] Login error: {e}")
        return None

def test_form_xss(url, form, session, payloads):
    vulnerabilities = []
    action = urljoin(url, form['action']) if form['action'] else url
    method = form.get('method', 'get').lower()
    
    for payload in payloads:
        for input_field in form['inputs']:
            # Notice we added 'textarea' here to catch Stored XSS!
            if input_field['type'] in ['text', 'hidden', 'password', 'textarea']:
                name = input_field['name']
                if not name:
                    continue
                
                data = {}
                for inp in form['inputs']:
                    data[inp['name']] = inp.get('value', '') if inp['name'] != name else payload
                
                try:
                    if method == 'post':
                        response = session.post(action, data=data)
                        test_url = action
                    else:
                        response = session.get(action, params=data)
                        test_url = response.url  
                    
                    print(f"    Testing payload: {payload[:30]}...")
                    
                    # --- XSS REFLECTION DETECTION ---
                    # If the exact payload string survives and is printed in the HTML response
                    if payload in response.text:
                        vuln = {
                            'url': url,
                            'form_action': action,
                            'method': method,
                            'vulnerable_input': name,
                            'payload': payload,
                            'error_detected': "Payload reflected in HTML response",
                            'remediation': "Use context-aware output encoding (e.g., htmlspecialchars() in PHP) to sanitize user input before rendering it in the browser."
                        }
                        vulnerabilities.append(vuln)
                        print(f"  [!] XSS Found: Input '{name}' with Payload '{payload}'")
                        
                except requests.RequestException as e:
                    print(f"[-] Error testing {url}: {e}")
    
    return vulnerabilities

def main():
    if len(sys.argv) < 3:
        print("Usage: python xss_tester.py <base_url> <login_url> [crawler_output]")
        print("Example: python xss_tester.py http://localhost http://localhost/login.php result.json")
        sys.exit(1)
    
    base_url = sys.argv[1]
    login_url = sys.argv[2]
    crawler_output = sys.argv[3] if len(sys.argv) > 3 else 'result.json'
    
    session = login_dvwa(base_url, login_url)
    if not session:
        sys.exit(1)
    
    try:
        # Load the map generated by your crawler
        with open(crawler_output, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"[-] Crawler output file '{crawler_output}' not found. Run the crawler first.")
        sys.exit(1)
    
    all_vulnerabilities = []
    
    print("\n[+] Starting AI-Driven XSS Tests...")
    # Extract forms properly depending on your result.json structure
    # Based on your previous crawler output, forms are inside a top-level "forms" array
    forms_to_test = data.get('forms', [])
    
    if not forms_to_test:
        print("[-] No forms found in result.json to test.")
        sys.exit(1)

    for form in forms_to_test:
        action = form.get('action', '')
        
        # Only test vulnerability endpoints to speed up the scan
        if 'vulnerabilities' in action:
            print(f"\n[*] Requesting AI payloads for form at: {action}")
            dynamic_payloads = generate_llm_xss_payloads(form)
            print(f"[*] AI generated {len(dynamic_payloads)} payloads. Testing now...")
            
            vulns = test_form_xss(action, form, session, dynamic_payloads)
            all_vulnerabilities.extend(vulns)
    
    with open('modules/xss_vulnerabilities.json', 'w') as f:
        json.dump(all_vulnerabilities, f, indent=4)
    
    print(f"\n[+] Testing complete. Found {len(all_vulnerabilities)} vulnerabilities.")
    print("[+] Results saved to modules/xss_vulnerabilities.json")

if __name__ == "__main__":
    main()