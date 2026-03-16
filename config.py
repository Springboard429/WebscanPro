"""
Configuration settings for WebScanPro
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.absolute()

# Request settings
REQUEST_TIMEOUT = 10  # seconds (increased for better connectivity)
MAX_REDIRECTS = 3  # increased from 2
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) WebScanPro/1.0"
DEFAULT_HEADERS = {
    'User-Agent': USER_AGENT,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Crawler settings
MAX_DEPTH = 1  # reduced from 2 for faster scanning
MAX_PAGES = 15  # reduced from 30 for faster scanning
MAX_THREADS = 10
FOLLOW_EXTERNAL_LINKS = False
RATE_LIMIT = 3  # requests per second (increased for faster scanning)

# File extensions to exclude
EXCLUDE_EXTENSIONS = [
    '.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx',
    '.xls', '.xlsx', '.ppt', '.pptx', '.zip', '.rar', '.tar.gz',
    '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm',
    '.woff', '.woff2', '.ttf', '.eot', '.otf', '.svg', '.ico'
]

# MIME types to exclude
EXCLUDE_MIME_TYPES = [
    'image/', 'video/', 'audio/', 'font/', 'application/octet-stream',
    'application/pdf', 'application/msword', 'application/vnd.ms-excel',
    'application/vnd.ms-powerpoint', 'application/zip', 'application/x-rar-compressed'
]

# Payload files
PAYLOAD_FILES = {
    'sql': os.path.join(BASE_DIR, 'data/payloads/sql_payloads.txt'),
    'xss': os.path.join(BASE_DIR, 'data/payloads/xss_payloads.txt'),
    'auth': os.path.join(BASE_DIR, 'data/payloads/auth_payloads.txt'),
    'idor': os.path.join(BASE_DIR, 'data/payloads/idor_payloads.txt'),
    'lfi': os.path.join(BASE_DIR, 'data/payloads/lfi_payloads.txt'),
    'rce': os.path.join(BASE_DIR, 'data/payloads/rce_payloads.txt'),
    'ssrf': os.path.join(BASE_DIR, 'data/payloads/ssrf_payloads.txt'),
    'xxe': os.path.join(BASE_DIR, 'data/payloads/xxe_payloads.txt')
}

# Scanner settings
SCAN_METHODS = {
    'sql': True,        # SQL Injection
    'xss': True,        # Cross-Site Scripting
    'idor': True,       # Insecure Direct Object Reference
    'lfi': True,        # Local File Inclusion
    'rce': True,        # Remote Code Execution
    'ssrf': True,       # Server-Side Request Forgery
    'xxe': True,        # XML External Entity
    'auth': True,       # Authentication Bypass
    'jwt': True,        # JWT Vulnerabilities
    'cors': True,       # CORS Misconfiguration
    'crlf': True,       # CRLF Injection
    'ssi': True,        # Server-Side Includes
    'ssti': True,       # Server-Side Template Injection
    'redirect': True,   # Open Redirect
    'header': True,     # Security Headers Check
    'csp': True,        # Content Security Policy
    'hsts': True,       # HTTP Strict Transport Security
    'clickjacking': True, # Clickjacking Protection
    'cookies': True,    # Cookie Security
    'csrf': True,       # CSRF Protection
    'backup': True,     # Backup Files
    'dir': True,        # Directory Listing
    'git': True,        # Git Repository
    'svn': True,        # SVN Repository
    'ds_store': True,   # .DS_Store Files
    'config': True,     # Configuration Files
    'log': True,        # Log Files
    'admin': True,      # Admin Panels
    'login': True,      # Login Pages
    'api': True,        # API Endpoints
    'graphql': True,    # GraphQL Endpoints
    'websocket': True,  # WebSocket Endpoints
    'sensitive': True,  # Sensitive Data Exposure
    'info': True,       # Information Disclosure
    'misc': True,       # Miscellaneous
}

# Report settings
REPORT_DIR = os.path.join(BASE_DIR, 'reports')
REPORT_TEMPLATE = os.path.join(BASE_DIR, 'reports/templates/report_template.html')
REPORT_STYLES = os.path.join(BASE_DIR, 'reports/templates/style.css')
REPORT_FORMATS = ['html', 'pdf', 'json', 'csv']

# Logging settings
LOG_LEVEL = 'INFO'
LOG_FILE = os.path.join(BASE_DIR, 'logs/webscanpro.log')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 5

# Database settings (if needed)
DATABASE = {
    'engine': 'sqlite',  # sqlite, mysql, postgresql
    'name': os.path.join(BASE_DIR, 'data/webscanpro.db'),
    'user': '',
    'password': '',
    'host': 'localhost',
    'port': '',
    'echo': False
}

# API keys (if needed)
API_KEYS = {
    'virustotal': '',
    'shodan': '',
    'censys': '',
    'binaryedge': '',
    'securitytrails': '',
    'fofa': '',
    'zoomeye': '',
    'hunter': '',
    'leaklookup': '',
    'dehashed': ''
}

# Proxy settings
PROXY = {
    'http': '',  # e.g., 'http://user:pass@proxy:port'
    'https': '',  # e.g., 'https://user:pass@proxy:port'
    'no_proxy': 'localhost,127.0.0.1'
}

# Rate limiting
RATE_LIMIT_ENABLED = True
RATE_LIMIT_REQUESTS = 10  # requests
RATE_LIMIT_PERIOD = 1  # second

# Request headers to test for security issues
HEADERS_TO_TEST = [
    'X-Forwarded-For',
    'X-Forwarded-Host',
    'X-Forwarded-Server',
    'X-Rewrite-URL',
    'X-Original-URL',
    'X-Originating-IP',
    'X-Remote-IP',
    'X-Remote-Addr',
    'X-Host',
    'X-HTTP-Host-Override',
    'X-ProxyUser-Ip',
    'X-WAP-Profile',
    'Proxy-Host',
    'Proxy-Connection',
    'Origin',
    'Referer',
    'Accept',
    'Accept-Encoding',
    'Accept-Charset',
    'Accept-Datetime',
    'Accept-Language',
    'Cache-Control',
    'Connection',
    'Content-Length',
    'Content-MD5',
    'Content-Type',
    'Date',
    'Expect',
    'From',
    'Host',
    'If-Match',
    'If-Modified-Since',
    'If-None-Match',
    'If-Range',
    'If-Unmodified-Since',
    'Max-Forwards',
    'Pragma',
    'Proxy-Authorization',
    'Range',
    'TE',
    'Upgrade',
    'Via',
    'Warning'
]

# Security headers to check
SECURITY_HEADERS = [
    'Strict-Transport-Security',
    'X-Frame-Options',
    'X-Content-Type-Options',
    'X-XSS-Protection',
    'Content-Security-Policy',
    'X-Permitted-Cross-Domain-Policies',
    'Referrer-Policy',
    'Feature-Policy',
    'Permissions-Policy',
    'Cross-Origin-Embedder-Policy',
    'Cross-Origin-Opener-Policy',
    'Cross-Origin-Resource-Policy'
]

# File and directory patterns to check for
FILE_PATTERNS = {
    'backup': ['.bak', '.backup', '.old', '.orig', '.tmp', '.swp', '.swo'],
    'config': ['.config', '.conf', '.ini', '.properties', '.env', '.yaml', '.yml'],
    'log': ['.log', '.logs', '.txt', '.text'],
    'database': ['.sql', '.db', '.sqlite', '.sqlite3', '.mdb', '.accdb'],
    'git': ['.git/HEAD', '.git/config', '.git/description'],
    'svn': ['.svn/entries'],
    'ds_store': ['.DS_Store'],
    'ide': ['.idea/', '.vscode/', '.project', '.classpath', '.settings/'],
    'temp': ['~', '.swp', '.swo', '.swn', '.bak', '.tmp'],
    'sensitive': ['password', 'secret', 'key', 'token', 'api_key', 'api-key', 'apikey'],
    'admin': ['admin', 'administrator', 'login', 'wp-admin', 'wp-login.php']
}

# Default ports for common services
DEFAULT_PORTS = {
    'http': 80,
    'https': 443,
    'ssh': 22,
    'ftp': 21,
    'sftp': 22,
    'mysql': 3306,
    'postgresql': 5432,
    'mongodb': 27017,
    'redis': 6379,
    'memcached': 11211,
    'elasticsearch': 9200,
    'vnc': 5900,
    'rdp': 3389,
    'smb': 445,
    'smtp': 25,
    'smtps': 465,
    'imap': 143,
    'imaps': 993,
    'pop3': 110,
    'pop3s': 995,
    'dns': 53,
    'ldap': 389,
    'ldaps': 636,
    'ntp': 123,
    'snmp': 161,
    'telnet': 23,
    'vnc': 5900,
    'x11': 6000
}

# Default credentials for common services
DEFAULT_CREDENTIALS = {
    'ftp': [('anonymous', 'anonymous@example.com'), ('admin', 'admin'), ('ftp', 'ftp')],
    'ssh': [('root', 'root'), ('admin', 'admin'), ('user', 'user')],
    'mysql': [('root', ''), ('root', 'root'), ('admin', 'admin')],
    'postgresql': [('postgres', 'postgres'), ('admin', 'admin')],
    'mssql': [('sa', ''), ('admin', 'admin')],
    'oracle': [('system', 'oracle'), ('sys', 'oracle')],
    'mongodb': [('admin', ''), ('admin', 'admin')],
    'redis': [('', '')],  # Redis often has no password
    'memcached': [('', '')],  # Memcached often has no password
    'elasticsearch': [('elastic', 'changeme'), ('admin', 'admin')],
    'vnc': [('', ''), ('admin', 'admin')],
    'rdp': [('Administrator', ''), ('admin', 'admin')],
    'smb': [('', ''), ('guest', ''), ('admin', 'admin')],
    'smtp': [('', ''), ('admin', 'admin')],
    'imap': [('', ''), ('admin', 'admin')],
    'pop3': [('', ''), ('admin', 'admin')],
    'telnet': [('root', ''), ('admin', 'admin')]
}

# Default wordlists for directory and file brute-forcing
WORDLISTS = {
    'directories': os.path.join(BASE_DIR, 'data/wordlists/directories.txt'),
    'files': os.path.join(BASE_DIR, 'data/wordlists/files.txt'),
    'extensions': os.path.join(BASE_DIR, 'data/wordlists/extensions.txt'),
    'usernames': os.path.join(BASE_DIR, 'data/wordlists/usernames.txt'),
    'passwords': os.path.join(BASE_DIR, 'data/wordlists/passwords.txt'),
    'subdomains': os.path.join(BASE_DIR, 'data/wordlists/subdomains.txt')
}

# Create necessary directories
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'data/payloads'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'data/wordlists'), exist_ok=True)