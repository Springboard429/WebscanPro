import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

BASE_URL = "http://localhost:8080/"
LOGIN_URL = BASE_URL + "login.php"

session = requests.Session()
visited = set()
forms_data = []

# ---------------- LOGIN ---------------- #

login_page = session.get(LOGIN_URL)
soup = BeautifulSoup(login_page.text, "html.parser")

user_token = soup.find("input", {"name": "user_token"})["value"]

login_data = {
    "username": "admin",
    "password": "password",
    "Login": "Login",
    "user_token": user_token
}

session.post(LOGIN_URL, data=login_data)

# ---------------- CRAWLER FUNCTION ---------------- #

def crawl(url):
    if url in visited:
        return
    
    if not url.startswith(BASE_URL):
        return
    
    visited.add(url)
    
    try:
        response = session.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
    except:
        return
    
    # -------- Extract Forms -------- #
    forms = soup.find_all("form")
    
    for form in forms:
        form_details = {}
        form_details["page"] = url
        form_details["action"] = urljoin(url, form.get("action"))
        form_details["method"] = form.get("method", "get").lower()
        
        inputs = []
        for input_tag in form.find_all("input"):
            input_details = {
                "name": input_tag.get("name"),
                "type": input_tag.get("type", "text")
            }
            inputs.append(input_details)
        
        form_details["inputs"] = inputs
        forms_data.append(form_details)
    
    # -------- Extract Links -------- #
    links = soup.find_all("a")
    for link in links:
        href = link.get("href")
        if href:
            full_url = urljoin(BASE_URL, href)
            crawl(full_url)

# ---------------- START CRAWLING ---------------- #

crawl(BASE_URL)

# ---------------- SAVE JSON ---------------- #

with open("output.json", "w") as f:
    json.dump(forms_data, f, indent=4)

print("Crawling Completed. Data saved to output.json")