import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json

BASE_URL = "http://localhost/"
LOGIN_URL = urljoin(BASE_URL, "login.php")
START_URL = urljoin(BASE_URL, "index.php")

USERNAME = "admin"
PASSWORD = "password"

session = requests.Session()

def login():
    print("[+] Opening login page...")
    response = session.get(LOGIN_URL)
    soup = BeautifulSoup(response.text, "html.parser")

    user_token = soup.find("input", {"name": "user_token"})
    token_value = user_token["value"] if user_token else ""

    login_data = {
        "username": USERNAME,
        "password": PASSWORD,
        "Login": "Login",
        "user_token": token_value
    }

    response = session.post(LOGIN_URL, data=login_data)

    if "Logout" in response.text:
        print("[+] Login successful!")
    else:
        print("[-] Login failed!")
        exit()


def is_internal(url):
    return urlparse(url).netloc == urlparse(BASE_URL).netloc

def extract_forms(soup):
    forms = []

    for form in soup.find_all("form"):
        form_data = {
            "action": form.get("action"),
            "method": form.get("method", "get").lower(),
            "inputs": [],
            "buttons": []
        }

        for input_tag in form.find_all(["input", "textarea", "select"]):
            input_type = input_tag.get("type", "").lower()

            input_data = {
                "tag": input_tag.name,
                "type": input_type,
                "name": input_tag.get("name"),
                "value": input_tag.get("value")
            }

            if input_tag.name == "input" and input_type in ["submit", "button", "reset", "image"]:
                form_data["buttons"].append(input_data)
            else:
                form_data["inputs"].append(input_data)

        for button_tag in form.find_all("button"):
            button_data = {
                "tag": "button",
                "type": button_tag.get("type", "submit"),
                "name": button_tag.get("name"),
                "value": button_tag.get("value"),
                "text": button_tag.get_text(strip=True)
            }
            form_data["buttons"].append(button_data)

        forms.append(form_data)

    return forms

def crawl():
    visited = set()
    all_found_urls = set()
    to_visit = [START_URL]
    crawl_results = []

    while to_visit:
        url = to_visit.pop(0)

        if url in visited:
            continue

        print(f"[+] Crawling: {url}")
        visited.add(url)
        all_found_urls.add(url)

        try:
            response = session.get(url)
        except:
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        page_links = []

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            full_url = urljoin(url, href)

            full_url = full_url.split("#")[0]

            if is_internal(full_url):
                page_links.append(full_url)
                all_found_urls.add(full_url)

                if full_url not in visited:
                    to_visit.append(full_url)

        forms = extract_forms(soup)

        crawl_results.append({
            "url": url,
            "links_on_page": list(set(page_links)),
            "forms_on_page": forms
        })

    return crawl_results, list(all_found_urls)


def save_results(pages_data, all_urls):
    final_data = {
        "total_unique_urls": len(all_urls),
        "all_urls": all_urls,
        "pages": pages_data
    }

    with open("full_crawl_results.json", "w") as f:
        json.dump(final_data, f, indent=4)

    print(f"[+] {len(all_urls)} unique URLs saved.")
    print("[+] Full data saved to full_crawl_results.json")


if __name__ == "__main__":
    login()
    pages_data, all_urls = crawl()
    save_results(pages_data, all_urls)