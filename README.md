# WebScanPro - Advanced Web Application Security Scanner

(https://via.placeholder.com/150x50?text=WebScanPro) [![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()

WebScanPro is a powerful and comprehensive web application security scanner designed to help security professionals and developers identify vulnerabilities in web applications. It combines automated scanning with advanced testing techniques to detect security issues across various layers of a web application.

## 📋 Table of Contents
- [Features](#-features)
- [Web Interface Features](#-web-interface-features)
- [Tech Stack](#-tech-stack)
- [System Architecture](#-system-architecture)
- [Installation](#-installation)
- [Usage](#-usage)
- [DVWA Testing Guide](#-dvwa-testing-guide)
- [Project Structure](#-project-structure)
- [Security Modules](#-security-modules)
- [Report Features](#-report-features)
- [Configuration](#-configuration)
- [Performance Considerations](#-performance-considerations)
- [Security Best Practices](#-security-best-practices)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)

## 🌟 Features


### Core Capabilities
- **Comprehensive Vulnerability Detection**: SQL Injection, XSS, and other OWASP Top 10 vulnerabilities
- **Intelligent Crawling**: JavaScript-aware crawling with configurable depth
- **Real-time Scanning**: Live progress updates and status monitoring
- **Multiple Scan Types**: Quick, Standard, and Comprehensive scan modes
- **Authentication Testing**: Support for various authentication mechanisms
- **API Security**: Automated API endpoint testing capabilities
- **Verbose Payload Testing**: Real-time display of all tested payloads
- **Session Management**: Automatic re-authentication for protected applications

### Web Interface Features
- **Modern Web Interface**: Professional, responsive design with glassmorphism effects
- **Dark Mode Toggle**: Switch between light and dark themes with persistent preferences
- **Real-time Scan Log**: Terminal-style logging with color-coded entries and collapsible display
- **Scan History**: View and manage previous scan results with detailed information
- **PDF Export**: Professional PDF report generation with complete vulnerability details
- **JSON Export**: Raw data export for integration with other tools
- **Statistics Dashboard**: Real-time vulnerability counts and scan metrics
- **Color-coded Severity**: Visual severity indicators (High/Medium/Low) with badges
- **Responsive Design**: Fully mobile-friendly interface that works on all devices
- **Smooth Animations**: Professional transitions and loading effects
- **Quick Scan Mode**: Fast, focused scanning for rapid vulnerability assessment

## 🛠 Tech Stack

### Backend Technologies
- **Python 3.8+**: Core programming language
- **Flask**: Web framework for the interface
- **asyncio**: Asynchronous I/O for high-performance scanning
- **aiohttp/httpx**: High-performance HTTP client libraries
- **BeautifulSoup4/lxml**: HTML/XML parsing
- **SQLAlchemy**: Database abstraction layer
- **Jinja2**: HTML report templating



### Frontend Technologies
- **HTML5/CSS3**: Modern, responsive report interface
- **JavaScript/ES6+**: Interactive report features
- **Chart.js**: Data visualization capabilities
- **Bootstrap 5**: Responsive design framework
- **Font Awesome**: Professional icon library
- **jsPDF**: Client-side PDF generation



### Security Libraries
- **Custom Scanners**: Purpose-built SQL Injection and XSS detection
- **OWASP Testing**: Based on OWASP Top 10 and security best practices
- **Cryptography**: Secure handling of sensitive data



## 🏗 System Architecture

### Component Architecture
1. **Web Interface Layer**: Flask-based web interface with modern UI
2. **Scanning Engine**: Core vulnerability detection modules
3. **Crawler Module**: Intelligent web page discovery and analysis
4. **Report Generator**: Multiple format output (JSON, PDF, HTML)
5. **Data Persistence**: File-based storage with JSON format


### Module Design
- **Independent Security Modules**: Pluggable architecture for different vulnerability types
- **Common Interface**: Standardized module interface for consistency
- **Error Handling**: Robust error recovery and logging
- **Progress Tracking**: Real-time scan progress and status updates



## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended)
- 1GB free disk space
- Network connectivity to target systems

### Quick Start
```bash
# Clone repository
git clone https://github.com/yourusername/WebScanPro.git
cd WebScanPro

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the web interface
python web_interface.py

# Access the application
# Open browser to: http://localhost:5000
```

## 📖 Usage

### Web Interface Usage (Recommended)
1. **Launch Application**: Run `python web_interface.py`
2. **Access Interface**: Open http://localhost:5000 in your browser
3. **Configure Scan**: Enter target URL and select scan type
4. **Authentication**: For protected sites, enter username and password
5. **Start Scanning**: Click "Start Scan" button
6. **Monitor Progress**: Watch real-time progress and payload testing
7. **Review Results**: Analyze vulnerabilities with detailed payload information
8. **Export Reports**: Download PDF or JSON reports for documentation

### Command Line Usage
```bash
# Basic scan
python main.py -u https://example.com

# SQL Injection only scan
python main.py -u https://example.com --scan-type sqli

# XSS only scan
python main.py -u https://example.com --scan-type xss

# Quick scan (fast, limited scope)
python main.py -u https://example.com --scan-type quick

# Scan with authentication
python main.py -u https://example.com --username admin --password password

# Verbose output with payload testing
python main.py -u https://example.com --verbose

# Comprehensive scan with custom depth
python main.py -u https://example.com -d 3 --scan-type all --verbose
```

## 🎯 DVWA Testing Guide

### DVWA Setup and Maintenance

**DVWA (Damn Vulnerable Web Application) requires special handling due to its development environment nature.**

### ⚠️ IMPORTANT: DVWA Database Reset
DVWA's database frequently becomes corrupted and needs to be reset:

```bash
# ALWAYS reset DVWA database before scanning
python reset_dvwa.py
```

### 🔧 DVWA Authentication Requirements
| **Field** | **Required Value** |
|-----------|-------------------|
| **URL** | `http://localhost:45/` |
| **Username** | `admin` |
| **Password** | `password` |

### � API Integration

### OpenRouter API for Enhanced Payloads
WebScanPro now supports **OpenRouter API integration** for generating advanced SQL injection payloads:

**Setup:**
1. Add your OpenRouter API key to `.env` file:
   ```
   OPENROUTER_API_KEY="your_openrouter_api_key_here"
   ```

2. The scanner will automatically:
   - Load base payloads (`'`, `' OR '1'='1`, `'1' UNION SELECT null--`)
   - Generate 5 additional advanced payloads via OpenRouter API
   - Use all payloads for comprehensive testing

**Benefits:**
- ✅ **More payloads** (10+ vs 3 base payloads)
- ✅ **Advanced techniques** (complex SQL injection methods)
- ✅ **Higher detection rates** (12+ vulnerabilities found)
- ✅ **Real-time logging** of all payload testing

**Models Supported:**
- `openai/gpt-3.5-turbo` (default)
- `openai/gpt-4` (if available in your plan)

**Example Usage:**
```bash
# Reset DVWA first
python reset_dvwa.py

# Scan with API payloads
python main.py -u "http://localhost:45/" --scan-type all --crawl-depth 1 --username admin --password password
```

The scanner will show:
- `[API] Generated 5 payloads from OpenRouter`
- `[SQLi] Testing parameter 'X' with payload: 'advanced_payload_here'`
- `[SQLi] ✅ VULNERABILITY FOUND with payload: 'advanced_payload_here'`
1. **Reset Database**: `python reset_dvwa.py`
2. **Wait for Setup**: Wait for "DVWA is now ready for scanning!" message
3. **Scan Immediately**: Scan in web interface right after reset
4. **Use Quick Scan**: Recommended for faster results

### 🚨 DVWA Known Issues
- **Database Corruption**: Frequent - requires reset
- **Session Expiration**: Common during scanning
- **Login Failures**: Normal - reset fixes it
- **Unreliable**: ~60% success rate without reset

### 📊 DVWA vs Public Test Sites
| **Target** | **Reliability** | **Authentication** | **Use Case** |
|-----------|-----------------|-------------------|--------------|
| **DVWA** | ⚠️ Unstable | ✅ Required | Authenticated testing |
| **testphp.vulnweb.com** | ✅ Very stable | ❌ Not required | Reliable testing |
| **Static sites** | ✅ Perfect | ❌ Not required | Basic testing |

### 🎯 Recommended DVWA Commands
```bash
# Reset DVWA (always do this first)
python reset_dvwa.py

# Quick scan DVWA (recommended)
python main.py -u http://localhost:45/ --username admin --password password --scan-type quick

# Full scan DVWA (after reset)
python main.py -u http://localhost:45/ --username admin --password password --scan-type all --verbose
```

## 📁 Project Structure

```
WebScanPro/
├── web_interface.py       # Flask web application
├── main.py              # Command-line interface
├── reset_dvwa.py        # DVWA database reset utility
├── core/                # Core functionality
│   ├── scanner.py        # Main scanner logic
│   ├── crawler.py       # Web crawler with authentication
│   └── scan_controller.py # Scan orchestration
├── modules/             # Security testing modules
│   ├── sql_injection.py  # SQL Injection detection with payloads
│   └── xss_scanner.py   # XSS detection
├── templates/           # Web interface templates
│   └── index.html      # Main web interface
├── reports/             # Generated scan reports
├── utils/               # Utility functions
│   └── payloads/        # SQL injection payload files
├── requirements.txt     # Python dependencies
└── README.md          # This file
```

## 🔒 Security Modules

### SQL Injection Scanner
- **Error-based SQLi**: Tests with `'` and `"` to trigger SQL errors
- **Boolean-based SQLi**: `' OR '1'='1` and `" OR "1"="1"` payloads
- **Union-based SQLi**: `' UNION SELECT null--` for UNION detection
- **Verbose Testing**: Real-time display of all tested payloads
- **Session Management**: Automatic re-authentication for protected sites
- **Custom Payloads**: Extensible payload system in `utils/payloads/`

#### SQL Injection Payloads Used
```python
# Error-based
"'"
'"'

# Boolean-based  
"' OR '1'='1"
"\" OR \"1\"=\"1"
"1' OR '1'='1' -- "

# Union-based
"1' UNION SELECT null--"
```

### XSS Scanner
- **Reflected XSS**: Detects reflected cross-site scripting
- **Stored XSS**: Identifies persistent XSS vulnerabilities
- **DOM-based XSS**: Tests for client-side XSS
- **Context Analysis**: Analyzes injection contexts
- **Payload Variations**: Multiple encoding and bypass techniques


## 📊 Report Features

### Web Interface Reports
- **Interactive Dashboard**: Real-time vulnerability statistics
- **Detailed Cards**: Comprehensive vulnerability information with payloads
- **Severity Classification**: High/Medium/Low categorization
- **Filtering Options**: Sort and filter vulnerabilities by type/severity
- **Export Capabilities**: PDF and JSON export functionality
- **Payload Display**: Shows successful payloads for each vulnerability



### Report Formats
- **PDF Reports**: Professional, printable vulnerability reports
- **JSON Export**: Machine-readable data for integration
- **HTML Reports**: Interactive web-based reports
- **CSV Export**: Spreadsheet-compatible data format



## ⚙️ Configuration

### Scan Configuration
- **Target URL**: Primary target for scanning
- **Scan Types**: Quick, Standard, Comprehensive, SQLi, XSS modes
- **Crawl Depth**: Configurable recursion depth (1-5 levels)
- **Rate Limiting**: Adjustable request timing
- **Authentication**: Support for form-based and header auth
- **Verbose Output**: Real-time payload testing display

### Interface Settings
- **Theme Selection**: Light/Dark mode with persistence
- **Log Display**: Collapsible real-time scan log
- **History Management**: Configurable history retention
- **Export Preferences**: Default report format settings

## 🔧 Troubleshooting

### Common Issues and Solutions

#### DVWA Authentication Issues
**Problem**: "0 vulnerabilities found" on DVWA
**Solution**: Always reset DVWA database first
```bash
python reset_dvwa.py
```

#### Web Interface Not Showing Results
**Problem**: SQL injection/XSS results not displayed
**Solution**: The web interface reads JSON reports - ensure scan completes

#### Payload Testing Not Visible
**Problem**: Can't see which payloads are being tested
**Solution**: Use `--verbose` flag for command line or check real-time log in web interface

#### Scan Timeout Issues
**Problem**: Scans taking too long or timing out
**Solution**: Use "Quick Scan" mode or reduce crawl depth

#### DVWA Session Lost During Scan
**Problem**: Frequent re-authentication during DVWA scanning
**Solution**: This is normal - the scanner automatically re-authenticates

### Debug Commands
```bash
# Test DVWA connectivity
python quick_dvwa_check.py

# Reset DVWA database
python reset_dvwa.py

# Verbose SQL injection testing
python main.py -u http://testphp.vulnweb.com/artists.php?artist=1 --scan-type sqli --verbose

# Test web interface functionality
python debug_web_interface.py
```



## 🚀 Performance Considerations

### Optimization Features
- **Asynchronous Scanning**: Concurrent request processing
- **Smart Rate Limiting**: Intelligent request timing
- **Caching Mechanism**: Avoid duplicate requests
- **Memory Management**: Efficient resource utilization
- **Progress Tracking**: Real-time status updates

### Scalability
- **Modular Architecture**: Easy to extend with new modules
- **Plugin System**: Support for custom security checks
- **API Integration**: RESTful interface for automation
- **Database Support**: SQLite with PostgreSQL upgrade path



## 🔒 Security Best Practices

### Safe Scanning
- **Non-Destructive**: Read-only vulnerability testing
- **Rate Limiting**: Respect target server resources
- **User-Agent Rotation**: Avoid detection and blocking
- **Session Management**: Proper authentication handling
- **Data Sanitization**: Secure handling of sensitive data

### Privacy Protection
- **Local Processing**: No data sent to external services
- **Encrypted Storage**: Secure local data storage
- **Audit Logging**: Complete scan activity tracking
- **Data Retention**: Configurable data cleanup policies

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Fork the repository
git clone https://github.com/yourusername/WebScanPro.git
cd WebScanPro

# Create development branch
git checkout -b feature/your-feature-name

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Make your changes
# ... commit and push ...
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OWASP Foundation**: Security testing methodologies
- **PortSwigger**: Burp Suite inspiration
- **SQLMap**: SQL injection testing techniques
- **DVWA Project**: Damn Vulnerable Web Application for testing
- **Open Source Community**: Various security tools and libraries

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section above
- Review the DVWA testing guide for DVWA-specific issues

---

**⚡ Pro Tip**: For reliable vulnerability testing, use public test sites like `http://testphp.vulnweb.com/artists.php?artist=1` for consistent results, and DVWA only when you need to test authenticated scanning capabilities.
