from bs4 import BeautifulSoup
from typing import List
from urllib.parse import urlparse, parse_qs

from .models import FormInfo, InputField
from .parser import normalize_url, is_same_domain


class HTMLExtractor:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def extract_forms(self, html: str, page_url: str) -> List[FormInfo]:
        soup = BeautifulSoup(html, 'html.parser')
        forms = []

        for form in soup.find_all('form'):
            action = form.get('action', '')
            action = normalize_url(action, page_url) if action else page_url

            inputs = []
            for tag in form.find_all(['input', 'textarea', 'select']):
                name = tag.get('name', '')
                if not name:
                    continue

                input_type = tag.get('type', 'text').lower() if tag.name == 'input' else tag.name

                inputs.append(InputField(
                    name=name,
                    type=input_type,
                    value=tag.get('value', ''),
                    required=tag.get('required') is not None
                ))

            if inputs:
                forms.append(FormInfo(
                    action=action,
                    method=form.get('method', 'get').upper(),
                    inputs=inputs,
                    name=form.get('name', '')
                ))

        parsed = urlparse(page_url)
        if parsed.query:
            params = parse_qs(parsed.query)
            if params:
                if not forms:
                    inputs = []
                    for param_name in params:
                        inputs.append(InputField(
                            name=param_name,
                            type='text',
                            value='',
                            required=False
                        ))
                    if inputs:
                        forms.append(FormInfo(
                            action=page_url,
                            method='GET',
                            inputs=inputs,
                            name=''
                        ))

        return forms

    def extract_links(self, html: str, page_url: str, follow_external: bool = False) -> List[str]:
        soup = BeautifulSoup(html, 'html.parser')
        links = []

        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith(('javascript:', 'mailto:', 'tel:', '#')):
                continue

            url = normalize_url(href, page_url)
            if follow_external or is_same_domain(url, self.base_url):
                links.append(url)

        return list(set(links))

    def get_title(self, html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('title')
        return title.text.strip() if title else ''
