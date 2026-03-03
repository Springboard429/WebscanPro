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

def fetch_forms(url, session):
    """Return metadata for all forms found on the page at `url`.

    Each form entry includes its action, method and a list of fields.  The
    field list covers `<input>`, `<textarea>` and `<select>` elements so
    DVWA-style forms (which often use textareas/selects) are handled.
    """
    try:
        response = session.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        forms = []
        for form in soup.find_all('form'):
            form_info = {
                'action': form.get('action'),
                'method': form.get('method', 'get').lower(),
                'fields': []
            }

            # collect various field types
            for field in form.find_all(['input', 'textarea', 'select']):
                if field.name == 'input':
                    form_info['fields'].append({
                        'type': field.get('type'),
                        'name': field.get('name'),
                        'value': field.get('value')
                    })
                elif field.name == 'textarea':
                    form_info['fields'].append({
                        'type': 'textarea',
                        'name': field.get('name'),
                        'value': field.text
                    })
                elif field.name == 'select':
                    options = [opt.get('value') for opt in field.find_all('option')]
                    form_info['fields'].append({
                        'type': 'select',
                        'name': field.get('name'),
                        'options': options
                    })

            forms.append(form_info)

        return forms
    except requests.RequestException as e:
        print(f"Error fetching forms from {url}: {e}")
        return []


def main():
    session = requests.Session()

    login_url = "http://localhost/login.php"
    username = "admin"
    password = "password"

    print(f"Fetching login page from {login_url}...")
    login_page = session.get(login_url)
    if login_page.status_code != 200:
        print(f"Failed to load login page, status {login_page.status_code}")
        return

    soup = BeautifulSoup(login_page.text, 'html.parser')
    user_token = soup.find('input', {'name': 'user_token'})
    user_token_value = user_token['value'] if user_token else None
    print(f"User token: {user_token_value}")

    login_data = {
        'username': username,
        'password': password,
        'Login': 'Login'
    }
    if user_token_value:
        login_data['user_token'] = user_token_value

    print("Attempting to log in...")
    response = session.post(login_url, data=login_data)
    if response.status_code != 200:
        print(f"Login failed with status {response.status_code}")
        return

    print("Login successful")
    base_url = "http://localhost/index.php"
    urls = fetch_urls(base_url, session)

    print(f"Found {len(urls)} urls")
    for url in urls[:10]:
        print("  -", url)

    # gather forms from each page (including DVWA-specific fields)
    forms = []
    for url in urls:
        forms.extend(fetch_forms(url, session))

    print(f"Found {len(forms)} forms across all pages")
    for form in forms[:5]:
        print("  -", form)

    # build combined structure matching your example
    combined = {
        'urls': urls,
        'forms': []
    }
    for f in forms:
        combined['forms'].append({
            'action': f.get('action'),
            'method': f.get('method'),
            'inputs': [
                { 'name': fld.get('name'), 'type': fld.get('type') }
                for fld in f.get('fields', [])
            ]
        })

    with open('output.json', 'w') as f:
        json.dump(combined, f, indent=4)

    print("Combined data saved to output.json")


if __name__ == '__main__':
    main()