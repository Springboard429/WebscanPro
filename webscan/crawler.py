import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import Set, List, Dict
import logging

from .models import DiscoveredURL, FormInfo, ScanResult
from .extractor import HTMLExtractor
from .parser import normalize_url, should_exclude, get_base_url, is_same_domain
from .config import ScannerConfig

logger = logging.getLogger(__name__)

class WebCrawler:

    def __init__(self, config: ScannerConfig = None):
        self.config = config or ScannerConfig()
        self.session = None
        self.cookie_jar = aiohttp.CookieJar()
        self.visited: Set[str] = set()
        self.target_base = None
        self.session_info: Dict[str, str] = {}
        self.logged_in = False

    async def __aenter__(self):
        await self.start_session()
        return self

    async def __aexit__(self, *args):
        await self.close_session()

    async def start_session(self):
        self.session = aiohttp.ClientSession(
            headers={'User-Agent': self.config.user_agent},
            timeout=aiohttp.ClientTimeout(total=self.config.request_timeout),
            cookie_jar=self.cookie_jar,
            connector=aiohttp.TCPConnector(ssl=self.config.verify_ssl)
        )

    async def close_session(self):
        if self.session:
            await self.session.close()

    async def fetch(self, url: str) -> tuple:
        try:
            async with self.session.get(url) as resp:
                text = await resp.text()
                content_type = resp.headers.get('Content-Type', '')
                if ';' in content_type:
                    content_type = content_type.split(';')[0].strip()
                return text, resp.status, content_type
        except Exception as e:
            logger.warning(f"Error fetching {url}: {e}")
            return '', 0, ''

    async def login(self, login_url: str) -> bool:
        login_url = login_url or f"{self.target_base}/login.php"
        logger.info(f"Logging in to {login_url}")

        try:
            async with self.session.get(login_url) as resp:
                html = await resp.text()

            soup = BeautifulSoup(html, 'html.parser')
            form = soup.find('form')
            data = {}

            if form:
                for inp in form.find_all('input'):
                    name = inp.get('name', '')
                    if name and inp.get('type') != 'submit':
                        data[name] = inp.get('value', '')

            data['username'] = self.config.login_username
            data['password'] = self.config.login_password
            data['Login'] = 'Login'

            async with self.session.post(login_url, data=data, allow_redirects=True) as resp:
                html = await resp.text()

            self.logged_in = 'vulnerabilities' in html or 'logout' in html
            if not self.logged_in:
                idx_html = await (await self.session.get(f"{self.target_base}/index.php")).text()
                self.logged_in = 'vulnerabilities' in idx_html or 'logout' in idx_html

            if self.logged_in:
                self.cookie_jar.update_cookies(
                    {'security': 'low'}, 
                    response_url=aiohttp.helpers.URL(self.target_base)
                )
                logger.info("Forced DVWA security level to: low")

            for cookie in self.cookie_jar:
                if cookie.key == 'PHPSESSID':
                    self.session_info['cookie_name'] = 'PHPSESSID'
                    self.session_info['cookie_value'] = cookie.value
                elif cookie.key == 'security':
                    self.session_info['security_level'] = cookie.value

            logger.info(f"Login {'successful' if self.logged_in else 'failed'}")
            return self.logged_in

        except Exception as e:
            logger.error(f"Login error: {e}")
            return False

    async def crawl(self, target_url: str) -> ScanResult:
        self.target_base = get_base_url(target_url)
        result = ScanResult(target=self.target_base)

        if self.config.login_url or (self.config.login_username and self.config.login_password):
            await self.login(self.config.login_url or f"{self.target_base}/login.php")

        queue: List[tuple] = [(target_url, 0, None)]
        semaphore = asyncio.Semaphore(self.config.max_concurrent)

        async def process(url: str, depth: int, parent: str):
            async with semaphore:
                url = normalize_url(url, self.target_base)
                
                if 'logout.php' in url or 'setup.php' in url:
                    return

                if url in self.visited or should_exclude(url, self.config.exclude_patterns):
                    return

                self.visited.add(url)
                html, status, ctype = await self.fetch(url)

                if not html or 'text/html' not in ctype:
                    return

                title = BeautifulSoup(html, 'html.parser').title
                title = title.text.strip() if title else ''
                result.urls.append(DiscoveredURL(url=url, status_code=status, title=title, depth=depth))

                if status == 200:
                    extractor = HTMLExtractor(self.target_base)
                    forms = extractor.extract_forms(html, url)
                    seen_actions = set(existing.action for existing in result.forms)

                    for form in forms:
                        action = form.action
                        if 'login.php' in action and action != f"{self.target_base}/login.php":
                            continue
                        if '?' in action and action.count('?') == 1:
                            if 'instructions.php' in action or 'doc=' in action:
                                continue

                        if form.inputs and action not in seen_actions:
                            result.forms.append(form)
                            seen_actions.add(action)
                            for inp in form.inputs:
                                result.parameters.add(inp.name)

                    if depth < self.config.max_depth:
                        links = extractor.extract_links(html, url, self.config.follow_external_links)
                        for link in links:
                            if is_same_domain(link, self.target_base):
                                queue.append((link, depth + 1, url))

        while queue:
            tasks = []
            for _ in range(min(self.config.max_concurrent, len(queue))):
                if queue:
                    url, depth, parent = queue.pop(0)
                    tasks.append(asyncio.create_task(process(url, depth, parent)))

            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

        result.session = self.session_info
        self._result = result
        return result

    def get_stats(self) -> dict:
        forms_count = len(self._result.forms) if hasattr(self, '_result') else 0
        return {
            'urls_visited': len(self.visited),
            'urls_found': len(self.visited),
            'forms_found': forms_count,
            'logged_in': self.logged_in
        }