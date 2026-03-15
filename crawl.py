import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urlparse
import sys

def fetch_urls(base_url, session):
    try:
        response = session.get(base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        base_domain = urlparse(base_url).netloc
        links = set() 
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(base_url, href)
            if urlparse(full_url).netloc == base_domain:
                links.add(full_url)
        
        return list(links)
    except requests.RequestException as e:
        print(f"[-] Error fetching the page: {e}")
        return []

def fetch_forms(url, session):
    try:
        response = session.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        forms = []
        for form in soup.find_all('form'):
            form_data = {
                'action': form.get('action', ''),
                'method': form.get('method', 'get').lower(),
                'inputs': []
            }
            
            for tag in form.find_all(['input', 'textarea', 'select']):
                input_data = {
                    'name': tag.get('name', ''),
                    'type': tag.get('type', 'text') if tag.name == 'input' else tag.name,
                    'value': tag.get('value', '')
                }
                form_data['inputs'].append(input_data)
            forms.append(form_data)
        
        return forms
    except requests.RequestException as e:
        print(f"[-] Error fetching forms from {url}: {e}")
        return []

if __name__ == "__main__":
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = input("Enter the base URL to crawl (e.g., http://localhost/): ")

    session = requests.Session()

    if len(sys.argv) > 2:
        login_url = sys.argv[2]
        username = "admin"  
        password = "password"
        
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
            if response.status_code == 200 and "login.php" not in response.url:
                print("[+] Login successful.")
                
                session.cookies.set('security', 'low')
                print("[+] DVWA Security level set to: low")
                
            else:
                print("[-] Login failed. Check credentials or URL.")
                sys.exit(1)
        except Exception as e:
            print(f"[-] Login failed: {e}. Proceeding without login.")
    else:
        print("[!] No login URL provided. Proceeding without login.")

    print(f"[*] Crawling {base_url} for links...")
    urls = fetch_urls(base_url, session)
    print(f"[+] Found {len(urls)} unique internal links.")

    data = {}
    print("[*] Extracting forms from discovered URLs...")

    ignore_list = ['logout.php', 'setup.php']

    for url in urls:
        if any(ignored in url for ignored in ignore_list):
            print(f"[-] Skipping ignored URL: {url}")
            continue
            
        forms = fetch_forms(url, session)
        if forms: 
            data[url] = forms

    with open('urls_and_forms.json', 'w') as f:
        json.dump(data, f, indent=4)

    print(f"[+] Extraction complete. Data saved to urls_and_forms.json")