"""
Scan Controller Module for WebScanPro

This module coordinates the scanning process, manages scan states,
and orchestrates different security scanners.
"""
import time
from typing import List, Dict, Any, Optional
from enum import Enum, auto

from core.crawler import WebCrawler
from modules.sql_injection import SQLInjectionScanner
from modules.xss_scanner import XSSScanner
from utils.logger import setup_logger

class ScanStatus(Enum):
    """Enum representing the possible states of a scan."""
    PENDING = auto()
    RUNNING = auto()
    PAUSED = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()

class ScanController:
    """Controls and coordinates the scanning process."""
    
    def __init__(self, target_url: str, scan_id: str = None, crawl_depth: int = 2, username: str = None, password: str = None):
        """
        Initialize the ScanController.
        
        Args:
            target_url: The target URL to scan
            scan_id: Optional scan ID for tracking
            crawl_depth: Maximum depth to crawl (default: 2)
            username: Optional username for authentication
            password: Optional password for authentication
        """
        self.target_url = target_url
        self.scan_id = scan_id or f"scan_{int(time.time())}"
        self.status = ScanStatus.PENDING
        self.progress = 0
        self.vulnerabilities = []
        self.stats = {
            'pages_crawled': 0,
            'vulnerabilities_found': 0,
            'start_time': None,
            'end_time': None,
            'elapsed_time': None
        }
        
        # Initialize scanners
        self.crawler = WebCrawler(target_url, username, password)
        self.crawler.max_depth = crawl_depth  # Set the crawl depth
        self.sql_scanner = SQLInjectionScanner()
        self.xss_scanner = XSSScanner()
        
        # Set up logging
        self.logger = setup_logger('ScanController')
    
    def start_scan(self) -> Dict[str, Any]:
        """Start the scanning process."""
        try:
            self.status = ScanStatus.RUNNING
            self.stats['start_time'] = time.time()
            self.logger.info(f"Starting scan {self.scan_id} for {self.target_url}")
            
            # Step 1: Crawl the target website
            self.logger.info("Crawling target website...")
            pages = self.crawler.crawl()
            self.stats['pages_crawled'] = len(pages)
            self.progress = 20
            
            if not pages:
                self.logger.warning("No pages found to scan")
                self.status = ScanStatus.FAILED
                return self._get_scan_result()
            
            # Step 2: Run SQL Injection scan
            self.logger.info("Running SQL Injection scan...")
            sql_vulns = []
            for page in pages:
                # Scan URL parameters with fast concurrent method
                if 'params' in page:
                    url_vulns = self.sql_scanner.scan_url_parameters_fast(page['url'], page['params'], crawler=self.crawler)
                    sql_vulns.extend(url_vulns)
                    # Early termination if we found significant vulnerabilities
                    if len(sql_vulns) >= 10:
                        self.logger.info(f"Found {len(sql_vulns)} SQL injection vulnerabilities, moving to next scan phase...")
                        break
                # Scan forms (keep original method for forms as they're more complex)
                if 'forms' in page:
                    form_vulns = self.sql_scanner.scan_forms(page['forms'], crawler=self.crawler)
                    sql_vulns.extend(form_vulns)
                    # Early termination for forms too
                    if len(sql_vulns) >= 10:
                        self.logger.info(f"Found {len(sql_vulns)} SQL injection vulnerabilities, moving to next scan phase...")
                        break
            self.vulnerabilities.extend(sql_vulns)
            self.progress = 50
            
            # Step 3: Run XSS scan
            self.logger.info("Running XSS scan...")
            xss_vulns = []
            for page in pages:
                # Scan URL parameters
                if 'params' in page:
                    url_vulns = self.xss_scanner.scan_url_parameters(page['url'], page['params'])
                    xss_vulns.extend(url_vulns)
                # Scan forms
                if 'forms' in page:
                    form_vulns = self.xss_scanner.scan_forms(page['forms'])
                    xss_vulns.extend(form_vulns)
            self.vulnerabilities.extend(xss_vulns)
            self.progress = 80
            
            # Update statistics
            self.stats['vulnerabilities_found'] = len(self.vulnerabilities)
            self.stats['end_time'] = time.time()
            self.stats['elapsed_time'] = self.stats['end_time'] - self.stats['start_time']
            
            # Mark scan as completed
            self.status = ScanStatus.COMPLETED
            self.progress = 100
            self.logger.info(f"Scan completed. Found {len(self.vulnerabilities)} vulnerabilities")
            
            return self._get_scan_result()
            
        except Exception as e:
            self.status = ScanStatus.FAILED
            self.logger.error(f"Scan failed: {str(e)}", exc_info=True)
            raise
    
    def pause_scan(self) -> bool:
        """Pause the current scan."""
        if self.status == ScanStatus.RUNNING:
            self.status = ScanStatus.PAUSED
            self.logger.info("Scan paused")
            return True
        return False
    
    def resume_scan(self) -> bool:
        """Resume a paused scan."""
        if self.status == ScanStatus.PAUSED:
            self.status = ScanStatus.RUNNING
            self.logger.info("Scan resumed")
            return True
        return False
    
    def cancel_scan(self) -> bool:
        """Cancel the current scan."""
        if self.status in [ScanStatus.RUNNING, ScanStatus.PAUSED]:
            self.status = ScanStatus.CANCELLED
            self.logger.info("Scan cancelled by user")
            return True
        return False
    
    def get_scan_status(self) -> Dict[str, Any]:
        """Get the current status of the scan."""
        return {
            'scan_id': self.scan_id,
            'status': self.status.name,
            'progress': self.progress,
            'vulnerabilities_found': self.stats['vulnerabilities_found'],
            'pages_crawled': self.stats['pages_crawled'],
            'elapsed_time': self.stats.get('elapsed_time')
        }
    
    def _get_scan_result(self) -> Dict[str, Any]:
        """Get the complete scan result."""
        return {
            'scan_id': self.scan_id,
            'status': self.status.name,
            'target_url': self.target_url,
            'start_time': self.stats['start_time'],
            'end_time': self.stats.get('end_time'),
            'elapsed_time': self.stats.get('elapsed_time'),
            'pages_crawled': self.stats['pages_crawled'],
            'vulnerabilities_found': self.stats['vulnerabilities_found'],
            'vulnerabilities': self.vulnerabilities
        }
    
    def export_results(self, format: str = 'json') -> str:
        """
        Export scan results in the specified format.
        
        Args:
            format: Output format (json, html, csv)
            
        Returns:
            The exported data as a string
        """
        result = self._get_scan_result()
        
        if format.lower() == 'json':
            import json
            return json.dumps(result, indent=2)
        elif format.lower() == 'html':
            # Simple HTML report generation
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>WebScanPro Report - {self.target_url}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; }}
                    h1, h2, h3 {{ color: #333; }}
                    .vulnerability {{ margin-bottom: 20px; padding: 10px; border-left: 4px solid #e74c3c; }}
                    .info {{ margin: 10px 0; }}
                    .severity-high {{ color: #e74c3c; font-weight: bold; }}
                    .severity-medium {{ color: #f39c12; font-weight: bold; }}
                    .severity-low {{ color: #3498db; font-weight: bold; }}
                </style>
            </head>
            <body>
                <h1>WebScanPro Security Report</h1>
                <div class="info"><strong>Target URL:</strong> {self.target_url}</div>
                <div class="info"><strong>Scan ID:</strong> {self.scan_id}</div>
                <div class="info"><strong>Status:</strong> {self.status.name}</div>
                <div class="info"><strong>Vulnerabilities Found:</strong> {len(self.vulnerabilities)}</div>
                
                <h2>Vulnerabilities</h2>
                {"".join(self._format_vulnerability_html(vuln) for vuln in self.vulnerabilities)}
            </body>
            </html>
            """
            return html
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _format_vulnerability_html(self, vuln: Dict[str, Any]) -> str:
        """Format a single vulnerability as HTML."""
        severity_class = f"severity-{vuln.get('severity', 'medium').lower()}"
        return f"""
        <div class="vulnerability">
            <h3><span class="{severity_class}">{vuln.get('type', 'Unknown')}</span> - {vuln.get('severity', 'Medium')}</h3>
            <div><strong>URL:</strong> {vuln.get('url', 'N/A')}</div>
            <div><strong>Parameter:</strong> {vuln.get('parameter', 'N/A')}</div>
            <div><strong>Method:</strong> {vuln.get('method', 'N/A')}</div>
            <div><strong>Payload:</strong> <code>{vuln.get('payload', 'N/A')}</code></div>
            <div><strong>Description:</strong> {vuln.get('description', 'No description available')}</div>
            <div><strong>Recommendation:</strong> {vuln.get('recommendation', 'No recommendation available')}</div>
        </div>
        """