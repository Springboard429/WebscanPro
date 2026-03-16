"""
Report Generator for WebScanPro

This module provides functionality to generate various types of reports
for the WebScanPro application.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from pathlib import Path

# Set up logger
logger = logging.getLogger('webscanpro.report_generator')

class ReportGenerator:
    """Base class for generating security scan reports."""
    
    def __init__(self, output_dir: str = "reports"):
        """
        Initialize the ReportGenerator.
        
        Args:
            output_dir: Directory to save the generated reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_report(self, scan_results: Dict[str, Any], report_type: str = "html", **kwargs) -> str:
        """
        Generate a report based on the scan results.
        
        Args:
            scan_results: Dictionary containing scan results
            report_type: Type of report to generate (html, pdf, json, excel)
            **kwargs: Additional keyword arguments for specific report types
            
        Returns:
            str: Path to the generated report file
        """
        report_methods = {
            'html': self.generate_html_report,
            'pdf': self.generate_pdf_report,
            'json': self.generate_json_report,
            'excel': self.generate_excel_report
        }
        
        if report_type not in report_methods:
            raise ValueError(f"Unsupported report type: {report_type}")
        
        # Generate a timestamp for the report filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"webscanpro_report_{timestamp}.{report_type}"
        report_path = self.output_dir / report_filename
        
        # Generate the report
        report_methods[report_type](scan_results, str(report_path), **kwargs)
        
        logger.info(f"Generated {report_type.upper()} report: {report_path}")
        return str(report_path)
    
    def generate_html_report(self, scan_results: Dict[str, Any], output_path: str, **kwargs) -> None:
        """
        Generate an HTML report.
        
        Args:
            scan_results: Dictionary containing scan results
            output_path: Path to save the HTML report
        """
        from . import html_report
        html_report.generate(scan_results, output_path, **kwargs)
    
    def generate_pdf_report(self, scan_results: Dict[str, Any], output_path: str, **kwargs) -> None:
        """
        Generate a PDF report.
        
        Args:
            scan_results: Dictionary containing scan results
            output_path: Path to save the PDF report
        """
        from . import pdf_report
        pdf_report.generate(scan_results, output_path, **kwargs)
    
    def generate_json_report(self, scan_results: Dict[str, Any], output_path: str, **kwargs) -> None:
        """
        Generate a JSON report.
        
        Args:
            scan_results: Dictionary containing scan results
            output_path: Path to save the JSON report
        """
        from . import json_report
        json_report.generate(scan_results, output_path, **kwargs)
    
    def generate_excel_report(self, scan_results: Dict[str, Any], output_path: str, **kwargs) -> None:
        """
        Generate an Excel report.
        
        Args:
            scan_results: Dictionary containing scan results
            output_path: Path to save the Excel report
        """
        from . import excel_report
        excel_report.generate(scan_results, output_path, **kwargs)

# Example usage
if __name__ == "__main__":
    # Example scan results
    example_results = {
        "scan_id": "scan_12345",
        "target": "https://example.com",
        "start_time": "2026-02-18T10:00:00+05:30",
        "end_time": "2026-02-18T10:30:00+05:30",
        "status": "completed",
        "vulnerabilities_found": 5,
        "vulnerabilities": [
            {
                "id": "vuln_001",
                "type": "SQL Injection",
                "severity": "High",
                "url": "https://example.com/search?q=test",
                "parameter": "q",
                "description": "SQL injection vulnerability found in the search parameter."
            },
            {
                "id": "vuln_002",
                "type": "XSS",
                "severity": "Medium",
                "url": "https://example.com/contact",
                "parameter": "message",
                "description": "Cross-site scripting (XSS) vulnerability found in the contact form."
            }
        ]
    }
    
    # Initialize the report generator
    report_gen = ReportGenerator()
    
    # Generate different types of reports
    html_report = report_gen.generate_report(example_results, "html")
    json_report = report_gen.generate_report(example_results, "json")
    
    print(f"Generated HTML report: {html_report}")
    print(f"Generated JSON report: {json_report}")