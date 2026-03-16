"""
JSON Report Generator for WebScanPro

This module provides functionality to generate JSON reports for security scan results.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import os

# Set up logger
logger = logging.getLogger('webscanpro.json_report')

def generate(scan_results: Dict[str, Any], output_path: str, **kwargs) -> None:
    """
    Generate a JSON report from scan results.
    
    Args:
        scan_results: Dictionary containing scan results
        output_path: Path to save the JSON report
        **kwargs: Additional keyword arguments (e.g., pretty_print, indent)
    """
    try:
        # Create a copy of scan_results to avoid modifying the original
        report_data = scan_results.copy()
        
        # Add metadata
        report_data['report_generated'] = datetime.now().isoformat()
        report_data['report_version'] = kwargs.get('version', '1.0.0')
        report_data['report_format'] = 'json'
        
        # Get formatting options
        indent = kwargs.get('indent', 2) if kwargs.get('pretty_print', True) else None
        
        # Ensure the output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Write the JSON file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=indent, default=str)
        
        logger.info(f"Generated JSON report: {output_path}")
        
    except Exception as e:
        logger.error(f"Error generating JSON report: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    # Example usage
    example_results = {
        "scan_id": "scan_12345",
        "target": "https://example.com",
        "start_time": "2026-02-18T10:00:00+05:30",
        "end_time": "2026-02-18T10:30:00+05:30",
        "status": "completed",
        "vulnerabilities_found": 2,
        "vulnerabilities": [
            {
                "id": "vuln_001",
                "type": "SQL Injection",
                "severity": "High",
                "url": "https://example.com/search?q=test",
                "parameter": "q",
                "description": "SQL injection vulnerability found in the search parameter.",
                "impact": "An attacker could extract sensitive information from the database.",
                "remediation": "Use parameterized queries or prepared statements.",
                "evidence": {
                    "request": "GET /search?q=test' OR '1'='1 HTTP/1.1\nHost: example.com",
                    "response_code": 500,
                    "response_body_snippet": "Error: You have an error in your SQL syntax..."
                },
                "references": [
                    "https://owasp.org/www-community/attacks/SQL_Injection"
                ]
            },
            {
                "id": "vuln_002",
                "type": "XSS",
                "severity": "Medium",
                "url": "https://example.com/contact",
                "parameter": "message",
                "description": "Cross-site scripting (XSS) vulnerability found in the contact form.",
                "impact": "An attacker could execute arbitrary JavaScript in the context of the user's browser.",
                "remediation": "Implement proper input validation and output encoding.",
                "evidence": {
                    "request": "POST /contact HTTP/1.1\nHost: example.com\nContent-Type: application/x-www-form-urlencoded\n\nname=test&message=<script>alert(1)</script>",
                    "response_code": 200,
                    "response_body_snippet": "<div class=\"message\"><script>alert(1)</script></div>"
                }
            }
        ]
    }
    
    # Generate the report
    generate(example_results, "example_report.json", pretty_print=True, version="1.0.0")
