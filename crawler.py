import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

BASE_URL = "http://localhost:80/"
LOGIN_URL = urljoin(BASE_URL, "login.php")
USERNAME = "admin"
PASSWORD = "password"

session = requests.Session()

# -------------------
# Login function
# -------------------
def login():
    print("[*] Logging in...")
    res = session.get(LOGIN_URL)
    soup = BeautifulSoup(res.text, "html.parser")
    token_input = soup.find("input", {"name": "user_token"})
    if not token_input:
        print("[!] User token not found. Check DVWA login page or security level.")
        return False
    token = token_input.get("value", "")
    data = {
        "username": USERNAME,
        "password": PASSWORD,
        "Login": "Login",
        "user_token": token
    }
    session.post(LOGIN_URL, data=data)
    print("[*] Login successful")
    return True

# -------------------
# Crawl pages recursively
# -------------------
def crawl(url, urls_set):
    if url in urls_set or not url.startswith(BASE_URL) and "localhost" not in url:
        return
    print(f"Crawling: {url}")
    urls_set.add(url)
    try:
        res = session.get(url)
    except:
        return
    soup = BeautifulSoup(res.text, "html.parser")
    
    # Extract all links
    for link in soup.find_all("a", href=True):
        href = link['href']
        full_url = urljoin(BASE_URL, href)
        crawl(full_url, urls_set)

# -------------------
# Extract all forms
# -------------------
def extract_forms(url):
    forms_list = []
    try:
        res = session.get(url)
    except:
        return forms_list
    soup = BeautifulSoup(res.text, "html.parser")
    for form in soup.find_all("form"):
        action = form.get("action")
        if action:
            action = urljoin(BASE_URL, action)
        method = form.get("method", "get").lower()
        inputs = []
        for inp in form.find_all("input"):
            name = inp.get("name")
            typ = inp.get("type", "text")
            inputs.append({"name": name, "type": typ})
        forms_list.append({
            "page": url,
            "action": action,
            "method": method,
            "inputs": inputs
        })
    return forms_list

# -------------------
# Main execution
# -------------------
if login():
    all_urls = set()
    crawl(BASE_URL, all_urls)

    all_urls = list(all_urls)
    all_urls.sort()

    all_forms = []
    for u in all_urls:
        if "localhost" in u:
            forms = extract_forms(u)
            all_forms.extend(forms)

    output = {
        "urls": all_urls,
        "forms": all_forms
    }

    with open("output.json", "w") as f:
        json.dump(output, f, indent=4)
    print("[*] Scan Completed")
    print("[*] Results saved in output.json")