from dataclasses import dataclass
from typing import List

EXCLUDE_PATTERNS = [
    r'\.pdf$', r'\.docx?$', r'\.xlsx?$', r'\.zip$', r'\.tar\.gz$',
    r'\.png$', r'\.jpg$', r'\.jpeg$', r'\.gif$', r'\.svg$', r'\.ico$',
    r'\.css$', r'\.js$', r'\.woff2?$',
]

@dataclass
class ScannerConfig:
    """Configuration options for the scanner."""
    max_depth: int = 3
    max_concurrent: int = 10
    request_timeout: int = 30
    exclude_patterns: List[str] = None

    user_agent: str = 'WebScanPro/1.0'
    verify_ssl: bool = False
    follow_external_links: bool = False

    login_url: str = None
    login_username: str = 'admin'
    login_password: str = 'password'

    def __post_init__(self):
        if self.exclude_patterns is None:
            self.exclude_patterns = EXCLUDE_PATTERNS.copy()
