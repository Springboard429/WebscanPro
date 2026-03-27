import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

def fetch_urls(base_url, session):
    try:
        response = session.get(base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(base_url, href)
            links.append(full_url)
        
        return links
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        return []

session = requests.Session()

login_url = "http://localhost:8080/login.php"
username = "admin"
password = "password"

login_page = session.get(login_url)
soup = BeautifulSoup(login_page.text, 'html.parser')

user_token = soup.find('input', {'name': 'user_token'})
if user_token:
    user_token_value = user_token['value']
else:
    user_token_value = None

login_data = {
    'username': username,
    'password': password,
    'Login': 'Login' 
}
if user_token_value:
    login_data['user_token'] = user_token_value

response = session.post(login_url, data=login_data)
if response.status_code != 200:
    print("Login failed")
    exit()

base_url = "http://localhost:8080/index.php"
urls = fetch_urls(base_url, session)

with open('urls.json', 'w') as f:
    json.dump(urls, f, indent=4)

print("URLs saved to urls.json")