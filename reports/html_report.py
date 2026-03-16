"""
HTML Report Generator for WebScanPro

This module provides functionality to generate HTML reports for security scan results.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

# Set up logger
logger = logging.getLogger('webscanpro.html_report')

# HTML template for the report
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebScanPro Security Report - {scan_target}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin: 0;
        }}
        .summary {{
            background-color: #f8f9fa;
            border-left: 5px solid #3498db;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 0 5px 5px 0;
        }}
        .vulnerability {{
            border: 1px solid #ddd;
            border-radius: 5px;
            margin-bottom: 15px;
            overflow: hidden;
        }}
        .vuln-header {{
            padding: 10px 15px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: bold;
        }}
        .vuln-high {{
            background-color: #f8d7da;
            border-left: 5px solid #dc3545;
        }}
        .vuln-medium {{
            background-color: #fff3cd;
            border-left: 5px solid #ffc107;
        }}
        .vuln-low {{
            background-color: #d1ecf1;
            border-left: 5px solid #17a2b8;
        }}
        .vuln-info {{
            background-color: #e2e3e5;
            border-left: 5px solid #6c757d;
        }}
        .vuln-details {{
            padding: 15px;
            border-top: 1px solid #ddd;
            display: none;
        }}
        .vuln-details.show {{
            display: block;
        }}
        .severity-badge {{
            display: inline-block;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.8em;
            font-weight: bold;
            color: white;
        }}
        .severity-high {{
            background-color: #dc3545;
        }}
        .severity-medium {{
            background-color: #ffc107;
        }}
        .severity-low {{
            background-color: #17a2b8;
        }}
        .severity-info {{
            background-color: #6c757d;
        }}
        .footer {{
            margin-top: 30px;
            padding: 20px;
            background-color: #f2f2f2;
            border-radius: 5px;
            text-align: center;
            color: #666;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f8f9fa;
            font-weight: bold;
        }}
        pre {{
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 3px;
            overflow-x: auto;
        }}
        .toggle-button {{
            background: none;
            border: none;
            font-size: 1.2em;
            cursor: pointer;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>WebScanPro Security Report</h1>
            <p>Generated on: {generated_date}</p>
        </div>
        
        <div class="summary">
            <h2>Scan Summary</h2>
            <p><strong>Target:</strong> {scan_target}</p>
            <p><strong>Scan ID:</strong> {scan_id}</p>
            <p><strong>Start Time:</strong> {start_time}</p>
            <p><strong>End Time:</strong> {end_time}</p>
            <p><strong>Status:</strong> {status}</p>
            <p><strong>Total Vulnerabilities Found:</strong> {vuln_count}</p>
            <div>
                <strong>Vulnerability Summary:</strong>
                <ul>
                    <li>High: <span class="severity-badge severity-high">{high_count}</span></li>
                    <li>Medium: <span class="severity-badge severity-medium">{medium_count}</span></li>
                    <li>Low: <span class="severity-badge severity-low">{low_count}</span></li>
                    <li>Info: <span class="severity-badge severity-info">{info_count}</span></li>
                </ul>
            </div>
        </div>
        
        <h2>Vulnerability Details</h2>
        {vulnerabilities_html}
        
        <div class="footer">
            <p>Report generated by WebScanPro - {version}</p>
        </div>
    </div>
    
    <script>
        // Toggle vulnerability details
        document.querySelectorAll('.vuln-header').forEach(header => {{
            header.addEventListener('click', function() {{
                const details = this.nextElementSibling;
                details.classList.toggle('show');
                const button = this.querySelector('.toggle-button');
                button.textContent = button.textContent === '+' ? '−' : '+';
            }});
        }});
    </script>
</body>
</html>
"""

def generate(scan_results: Dict[str, Any], output_path: str, **kwargs) -> None:
    """
    Generate an HTML report from scan results.
    
    Args:
        scan_results: Dictionary containing scan results
        output_path: Path to save the HTML report
        **kwargs: Additional keyword arguments (e.g., version, title)
    """
    try:
        # Extract data from scan results
        scan_target = scan_results.get('target', 'N/A')
        scan_id = scan_results.get('scan_id', 'N/A')
        start_time = scan_results.get('start_time', 'N/A')
        end_time = scan_results.get('end_time', 'N/A')
        status = scan_results.get('status', 'unknown').capitalize()
        vulnerabilities = scan_results.get('vulnerabilities', [])
        
        # Count vulnerabilities by severity
        vuln_count = len(vulnerabilities)
        high_count = sum(1 for v in vulnerabilities if v.get('severity', '').lower() == 'high')
        medium_count = sum(1 for v in vulnerabilities if v.get('severity', '').lower() == 'medium')
        low_count = sum(1 for v in vulnerabilities if v.get('severity', '').lower() == 'low')
        info_count = sum(1 for v in vulnerabilities if v.get('severity', '').lower() == 'info')
        
        # Generate HTML for each vulnerability
        vulnerabilities_html = []
        for vuln in vulnerabilities:
            vuln_id = vuln.get('id', '')
            vuln_type = vuln.get('type', 'Unknown')
            severity = vuln.get('severity', 'info').lower()
            description = vuln.get('description', 'No description available.')
            url = vuln.get('url', 'N/A')
            parameter = vuln.get('parameter', 'N/A')
            
            # Generate details HTML
            details_html = f"""
            <div class="vuln-details">
                <h3>Details</h3>
                <table>
                    <tr>
                        <th>ID</th>
                        <td>{vuln_id}</td>
                    </tr>
                    <tr>
                        <th>Type</th>
                        <td>{vuln_type}</td>
                    </tr>
                    <tr>
                        <th>URL</th>
                        <td><a href="{url}" target="_blank">{url}</a></td>
                    </tr>
                    <tr>
                        <th>Parameter</th>
                        <td><code>{parameter}</code></td>
                    </tr>
                    <tr>
                        <th>Description</th>
                        <td>{description}</td>
                    </tr>
                    <tr>
                        <th>Impact</th>
                        <td>{vuln.get('impact', 'N/A')}</td>
                    </tr>
                    <tr>
                        <th>Remediation</th>
                        <td>{vuln.get('remediation', 'No remediation information available.')}</td>
                    </tr>
            """
            
            # Add evidence if available
            if 'evidence' in vuln:
                evidence = vuln['evidence']
                details_html += f"""
                    <tr>
                        <th>Evidence</th>
                        <td>
                            <p><strong>Request:</strong></p>
                            <pre>{evidence.get('request', 'N/A')}</pre>
                            <p><strong>Response Code:</strong> {evidence.get('response_code', 'N/A')}</p>
                            <p><strong>Response Snippet:</strong></p>
                            <pre>{evidence.get('response_body_snippet', 'N/A')}</pre>
                        </td>
                    </tr>
                """
            
            # Add references if available
            if 'references' in vuln and vuln['references']:
                refs = '<br>'.join(f'<a href="{ref}" target="_blank">{ref}</a>' for ref in vuln['references'])
                details_html += f"""
                    <tr>
                        <th>References</th>
                        <td>{refs}</td>
                    </tr>
                """
            
            details_html += """
                </table>
            </div>
            """
            
            # Add the vulnerability to the list
            vulnerabilities_html.append(f"""
                <div class="vulnerability">
                    <div class="vuln-header vuln-{severity}">
                        <span>
                            <span class="severity-badge severity-{severity}">{severity.upper()}</span>
                            {vuln_type} - {description[:100]}{'...' if len(description) > 100 else ''}
                        </span>
                        <button class="toggle-button" aria-label="Toggle details">+</button>
                    </div>
                    {details_html}
                </div>
            """.format(severity=severity, vuln_type=vuln_type, 
                       description=description, details_html=details_html))
        
        # Format the HTML with the data
        html_content = HTML_TEMPLATE.format(
            scan_target=scan_target,
            generated_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            scan_id=scan_id,
            start_time=start_time,
            end_time=end_time,
            status=status,
            vuln_count=vuln_count,
            high_count=high_count,
            medium_count=medium_count,
            low_count=low_count,
            info_count=info_count,
            vulnerabilities_html='\n'.join(vulnerabilities_html) if vulnerabilities_html else '<p>No vulnerabilities found.</p>',
            version=kwargs.get('version', '1.0.0')
        )
        
        # Ensure the output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Write the HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Generated HTML report: {output_path}")
        
    except Exception as e:
        logger.error(f"Error generating HTML report: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    # Example usage
    example_results = {
        "scan_id": "scan_12345",
        "target": "https://example.com",
        "start_time": "2026-02-18T10:00:00+05:30",
        "end_time": "2026-02-18T10:30:00+05:30",
        "status": "completed",
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
    generate(example_results, "example_report.html", version="1.0.0")
