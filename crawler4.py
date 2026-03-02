import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urlparse

# CONFIGURATION

BASE_URL = "http://localhost:80/"
LOGIN_URL = urljoin(BASE_URL, "login.php")

USERNAME = "admin"
PASSWORD = "password"
# SESSION
session = requests.Session()

# LOGIN FUNCTION
def login():
    print(" Accessing login page...")

    try:
        response = session.get(LOGIN_URL, timeout=5)
    except:
        print(" DVWA is not running! Start Docker container first.")
        exit()

    soup = BeautifulSoup(response.text, "html.parser")

    token_input = soup.find("input", {"name": "user_token"})
    user_token = token_input["value"] if token_input else None

    login_data = {
        "username": USERNAME,
        "password": PASSWORD,
        "Login": "Login"
    }

    if user_token:
        login_data["user_token"] = user_token

    print("Attempting login...")
    login_response = session.post(LOGIN_URL, data=login_data)

    if "logout.php" in login_response.text:
        print("Login successful!\n")
    else:
        print(" Login failed! Check credentials or security level.")
        exit()


# crawler

visited = set()
collected_forms = set()

results = {
    "urls": [],
    "forms": []
}

def normalize_url(url):
    parsed = urlparse(url)
    return parsed.scheme + "://" + parsed.netloc + parsed.path

def crawl(url):
    normalized = normalize_url(url)

    if normalized in visited:
        return

    if "login.php" in normalized:
        return

    print(f"[+] Crawling: {normalized}")
    visited.add(normalized)
    results["urls"].append(normalized)

    try:
        response = session.get(normalized, timeout=5)
    except:
        return

    if response.status_code != 200:
        return

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract links
    for link in soup.find_all("a", href=True):
        full_url = urljoin(BASE_URL, link["href"])

        if full_url.startswith(BASE_URL):
            crawl(full_url)

    # Extract Forms
    for form in soup.find_all("form"):
        form_signature = str(form)

        if form_signature in collected_forms:
            continue

        collected_forms.add(form_signature)

        form_details = {
            "action": form.get("action"),
            "method": form.get("method", "GET").upper(),
            "inputs": []
        }

        for input_tag in form.find_all("input"):
            form_details["inputs"].append({
                "name": input_tag.get("name"),
                "type": input_tag.get("type")
            })

        results["forms"].append(form_details)

# ==============================
# MAIN
# ==============================

if __name__ == "__main__":
    print("\nDVWA Crawler Started\n")

    login()
    crawl(urljoin(BASE_URL, "index.php"))

    with open("urls.json", "w") as file:
        json.dump(results, file, indent=4)

    print("\n Crawling Completed.")
    print(f" Total URLs Found: {len(results['urls'])}")
    print(f"Total Forms Found: {len(results['forms'])}")
    print(" Data saved to urls.json")
