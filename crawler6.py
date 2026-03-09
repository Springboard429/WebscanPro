import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urlparse

# CONFIG

BASE_URL = "http://localhost/"
LOGIN_URL = urljoin(BASE_URL, "login.php")

USERNAME = "admin"
PASSWORD = "password"

session = requests.Session()

# LOGIN

def login():
    print("Accessing login page...")

    try:
        response = session.get(LOGIN_URL, timeout=5)
    except:
        print("DVWA is not running!")
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

    login_response = session.post(LOGIN_URL, data=login_data)

    if "logout.php" in login_response.text:
        print("Login successful!\n")
    else:
        print("Login failed!")
        exit()


# CRAWLER

visited = set()
collected_forms = set()

results = {
    "urls": [],
    "forms": [],
    "vulnerabilities": []
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

    print("Crawling:", normalized)

    visited.add(normalized)
    results["urls"].append(normalized)

    try:
        response = session.get(normalized, timeout=5)
    except:
        return

    if response.status_code != 200:
        return

    soup = BeautifulSoup(response.text, "html.parser")

    # LINKS
    links = soup.find_all("a", href=True)

    for link in links:
        full_url = urljoin(BASE_URL, link["href"])
        if full_url.startswith(BASE_URL):
            crawl(full_url)

    # FORMS
    forms = soup.find_all("form")

    for form in forms:

        form_signature = str(form)

        if form_signature in collected_forms:
            continue

        collected_forms.add(form_signature)

        action = form.get("action")

        if action:
            full_action = urljoin(normalized, action)
        else:
            full_action = normalized

        method = form.get("method", "GET").upper()

        form_details = {
            "action": full_action,
            "method": method,
            "inputs": []
        }

        inputs = form.find_all("input")

        for input_tag in inputs:
            form_details["inputs"].append({
                "name": input_tag.get("name"),
                "type": input_tag.get("type")
            })

        results["forms"].append(form_details)


# SQL INJECTION TEST

def test_sql_injection():

    print("\nStarting SQL Injection Testing...\n")

    vuln_count = 0

    TRUE_PAYLOAD = "1' OR '1'='1"
    FALSE_PAYLOAD = "1' AND '1'='2"

    for url in results["urls"]:

        if "sqli" not in url:
            continue

        print("Testing:", url)

        try:
            normal = session.get(url, params={"id": "1"}).text
            true_response = session.get(url, params={"id": TRUE_PAYLOAD}).text
            false_response = session.get(url, params={"id": FALSE_PAYLOAD}).text
        except:
            continue

        # NORMAL SQLI
        if true_response.count("First name") > normal.count("First name"):

            print("SQL Injection Detected (Normal)!")
            print("URL:", url)
            print("-" * 50)

            results["vulnerabilities"].append({
                "type": "SQL Injection",
                "url": url,
                "payload": TRUE_PAYLOAD
            })

            vuln_count += 1
            continue

        # BLIND SQLI
        if true_response != false_response:

            print("SQL Injection Detected (Blind)!")
            print("URL:", url)
            print("-" * 50)

            results["vulnerabilities"].append({
                "type": "Blind SQL Injection",
                "url": url,
                "payload": TRUE_PAYLOAD
            })

            vuln_count += 1
            continue

    print("\nTotal SQL Injection Vulnerabilities Detected:", vuln_count)


# MAIN

if __name__ == "__main__":

    print("\nDVWA Crawler Started\n")

    login()

    crawl(urljoin(BASE_URL, "index.php"))

    test_sql_injection()

    with open("urls.json", "w") as file:
        json.dump(results, file, indent=4)

    print("\nCrawling Completed.")
    print("Total URLs Found:", len(results["urls"]))
    print("Total Forms Found:", len(results["forms"]))
    print("Data saved to urls.json")
