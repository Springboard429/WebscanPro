"""
PDF Report Generator for WebScanPro

This module provides functionality to generate PDF reports for security scan results.
It uses the ReportLab library to create professional-looking PDF documents.
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

# Try to import ReportLab, but don't fail if it's not installed
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
        Image, ListFlowable, ListItem, PageTemplate, Frame, NextPageTemplate
    )
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.fonts import addMapping
    
    # Register fonts (you may need to adjust paths or register additional fonts)
    try:
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVuSans-Oblique', 'DejaVuSans-Oblique.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVuSans-BoldOblique', 'DejaVuSans-BoldOblique.ttf'))
        
        addMapping('DejaVuSans', 0, 0, 'DejaVuSans')
        addMapping('DejaVuSans', 1, 0, 'DejaVuSans-Bold')
        addMapping('DejaVuSans', 0, 1, 'DejaVuSans-Oblique')
        addMapping('DejaVuSans', 1, 1, 'DejaVuSans-BoldOblique')
        
        DEFAULT_FONT = 'DejaVuSans'
    except:
        DEFAULT_FONT = 'Helvetica'
    
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Set up logger
logger = logging.getLogger('webscanpro.pdf_report')

# Define styles
class PDFStyles:
    """Container for PDF styles."""
    
    def __init__(self):
        """Initialize styles."""
        self.styles = getSampleStyleSheet()
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='Title',
            parent=self.styles['Heading1'],
            fontSize=24,
            leading=28,
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName=f'{DEFAULT_FONT}-Bold',
            textColor=colors.HexColor('#2c3e50')
        ))
        
        # Heading styles
        self.styles.add(ParagraphStyle(
            name='Heading1',
            parent=self.styles['Heading1'],
            fontSize=18,
            leading=22,
            spaceAfter=12,
            fontName=f'{DEFAULT_FONT}-Bold',
            textColor=colors.HexColor('#2c3e50')
        ))
        
        self.styles.add(ParagraphStyle(
            name='Heading2',
            parent=self.styles['Heading2'],
            fontSize=14,
            leading=18,
            spaceAfter=8,
            fontName=f'{DEFAULT_FONT}-Bold',
            textColor=colors.HexColor('#34495e')
        ))
        
        self.styles.add(ParagraphStyle(
            name='Heading3',
            parent=self.styles['Heading3'],
            fontSize=12,
            leading=16,
            spaceAfter=6,
            fontName=f'{DEFAULT_FONT}-Bold',
            textColor=colors.HexColor('#7f8c8d')
        ))
        
        # Normal text style
        self.styles.add(ParagraphStyle(
            name='Normal',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=12,
            spaceAfter=6,
            fontName=DEFAULT_FONT
        ))
        
        # Code style
        self.styles.add(ParagraphStyle(
            name='Code',
            parent=self.styles['Code'],
            fontSize=8,
            leading=10,
            fontName='Courier',
            backColor=colors.HexColor('#f8f9fa'),
            borderWidth=1,
            borderColor=colors.HexColor('#dee2e6'),
            borderPadding=5
        ))
        
        # Footer style
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            leading=10,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#7f8c8d'),
            fontName=DEFAULT_FONT
        ))
        
        # Severity styles
        self.severity_styles = {
            'high': colors.HexColor('#dc3545'),
            'medium': colors.HexColor('#ffc107'),
            'low': colors.HexColor('#17a2b8'),
            'info': colors.HexColor('#6c757d')
        }

# Custom page template with header and footer
class PDFPageTemplate(PageTemplate):
    """Custom page template with header and footer."""
    
    def __init__(self, doc, title, version):
        """Initialize the page template."""
        self.title = title
        self.version = version
        self.page_count = 0
        
        # Create frames for the page
        frame = Frame(
            doc.leftMargin, 
            doc.bottomMargin, 
            doc.width, 
            doc.height - 1.5*cm,  # Leave space for header and footer
            leftPadding=0,
            rightPadding=0,
            bottomPadding=0,
            topPadding=0,
            id='normal'
        )
        
        super().__init__('main', [frame])
    
    def beforeDrawPage(self, canvas, doc):
        """Draw header and footer on each page."""
        self.page_count += 1
        
        # Save the current graphics state
        canvas.saveState()
        
        # Draw header
        canvas.setFont(f'{DEFAULT_FONT}-Bold', 14)
        canvas.setFillColor(colors.HexColor('#2c3e50'))
        canvas.drawString(doc.leftMargin, doc.pagesize[1] - 1*cm, self.title)
        
        # Draw header line
        canvas.setStrokeColor(colors.HexColor('#3498db'))
        canvas.setLineWidth(2)
        canvas.line(
            doc.leftMargin, 
            doc.pagesize[1] - 1.2*cm, 
            doc.pagesize[0] - doc.rightMargin, 
            doc.pagesize[1] - 1.2*cm
        )
        
        # Draw footer
        canvas.setFont(DEFAULT_FONT, 8)
        canvas.setFillColor(colors.HexColor('#7f8c8d'))
        
        # Left side: Page number
        canvas.drawString(
            doc.leftMargin, 
            0.5*cm, 
            f"Page {self.page_count}"
        )
        
        # Center: Report title and date
        canvas.drawCentredString(
            doc.pagesize[0] / 2, 
            0.5*cm, 
            f"{self.title} - Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        
        # Right side: Version
        canvas.drawRightString(
            doc.pagesize[0] - doc.rightMargin, 
            0.5*cm, 
            f"WebScanPro v{self.version}"
        )
        
        # Draw footer line
        canvas.setStrokeColor(colors.HexColor('#dee2e6'))
        canvas.setLineWidth(0.5)
        canvas.line(
            doc.leftMargin, 
            1*cm, 
            doc.pagesize[0] - doc.rightMargin, 
            1*cm
        )
        
        # Restore the graphics state
        canvas.restoreState()

def generate(scan_results: Dict[str, Any], output_path: str, **kwargs) -> None:
    """
    Generate a PDF report from scan results.
    
    Args:
        scan_results: Dictionary containing scan results
        output_path: Path to save the PDF report
        **kwargs: Additional keyword arguments (e.g., title, author, version)
    """
    if not REPORTLAB_AVAILABLE:
        logger.error("ReportLab is not installed. Please install it with 'pip install reportlab'")
        raise ImportError("ReportLab is required for PDF report generation.")
    
    try:
        # Get report metadata
        title = kwargs.get('title', 'WebScanPro Security Report')
        author = kwargs.get('author', 'WebScanPro')
        version = kwargs.get('version', '1.0.0')
        
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
        
        # Create the PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            leftMargin=1.5*cm,
            rightMargin=1.5*cm,
            topMargin=2.5*cm,
            bottomMargin=2*cm
        )
        
        # Set up styles
        styles = PDFStyles()
        
        # Set up the page template
        doc.addPageTemplates([PDFPageTemplate(doc, title, version)])
        
        # Create the story (content)
        story = []
        
        # Add title
        story.append(Paragraph(title, styles.styles['Title']))
        
        # Add scan summary
        story.append(Paragraph("Scan Summary", styles.styles['Heading1']))
        
        # Summary table
        summary_data = [
            ["Target:", scan_target],
            ["Scan ID:", scan_id],
            ["Start Time:", start_time],
            ["End Time:", end_time],
            ["Status:", status],
            ["Total Vulnerabilities:", str(vuln_count)],
            ["High Severity:", str(high_count)],
            ["Medium Severity:", str(medium_count)],
            ["Low Severity:", str(low_count)],
            ["Informational:", str(info_count)]
        ]
        
        summary_table = Table(summary_data, colWidths=[doc.width*0.3, doc.width*0.7])
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), DEFAULT_FONT),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('FONTWEIGHT', (0, 0), (0, -1), 'Bold'),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.5*cm))
        
        # Add vulnerability details
        if vulnerabilities:
            story.append(Paragraph("Vulnerability Details", styles.styles['Heading1']))
            
            for i, vuln in enumerate(vulnerabilities, 1):
                # Add a page break if this isn't the first vulnerability
                if i > 1:
                    story.append(PageBreak())
                
                # Vulnerability header
                vuln_id = vuln.get('id', f'VULN-{i}')
                vuln_type = vuln.get('type', 'Unknown')
                severity = vuln.get('severity', 'info').lower()
                description = vuln.get('description', 'No description available.')
                
                # Set the color based on severity
                severity_color = styles.severity_styles.get(severity, colors.HexColor('#6c757d'))
                
                # Add vulnerability title
                title_style = ParagraphStyle(
                    'VulnTitle',
                    parent=styles.styles['Heading2'],
                    backColor=severity_color,
                    textColor=colors.white if severity in ['high', 'medium'] else colors.black,
                    padding=6,
                    borderRadius=4
                )
                
                story.append(Paragraph(
                    f"{vuln_id}: {vuln_type}", 
                    title_style
                ))
                
                # Add severity badge
                severity_style = ParagraphStyle(
                    'SeverityBadge',
                    parent=styles.styles['Normal'],
                    fontName=f'{DEFAULT_FONT}-Bold',
                    fontSize=10,
                    textColor=colors.white,
                    backColor=severity_color,
                    borderWidth=1,
                    borderColor=severity_color,
                    borderPadding=4,
                    borderRadius=3,
                    alignment=TA_LEFT
                )
                
                story.append(Paragraph(
                    f"Severity: <font color='white'><b>{severity.upper()}</b></font>",
                    severity_style
                ))
                
                story.append(Spacer(1, 0.5*cm))
                
                # Add vulnerability details
                details_data = [
                    ["Description:", description],
                    ["URL:", vuln.get('url', 'N/A')],
                    ["Parameter:", vuln.get('parameter', 'N/A')],
                    ["Impact:", vuln.get('impact', 'N/A')],
                    ["Remediation:", vuln.get('remediation', 'No remediation information available.')]
                ]
                
                # Add evidence if available
                if 'evidence' in vuln:
                    evidence = vuln['evidence']
                    details_data.extend([
                        ["Evidence:", ""],
                        ["Request:", evidence.get('request', 'N/A')],
                        ["Response Code:", str(evidence.get('response_code', 'N/A'))],
                        ["Response Snippet:", evidence.get('response_body_snippet', 'N/A')]
                    ])
                
                # Add references if available
                if 'references' in vuln and vuln['references']:
                    refs = '\n'.join(f"• {ref}" for ref in vuln['references'])
                    details_data.append(["References:", refs])
                
                # Create the details table
                details_table = Table(
                    details_data, 
                    colWidths=[doc.width*0.25, doc.width*0.75],
                    hAlign='LEFT'
                )
                
                details_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, -1), DEFAULT_FONT),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                    ('FONTWEIGHT', (0, 0), (0, -1), 'Bold'),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
                    ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
                    ('SPAN', (0, 0), (1, 0)),  # Span the first row for the description
                    ('SPAN', (0, 1), (1, 1)),  # Span the second row for the URL
                    ('SPAN', (0, 2), (1, 2)),  # Span the third row for the parameter
                    ('SPAN', (0, 3), (1, 3)),  # Span the fourth row for the impact
                    ('SPAN', (0, 4), (1, 4)),  # Span the fifth row for the remediation
                ]))
                
                story.append(details_table)
        else:
            story.append(Paragraph("No vulnerabilities found.", styles.styles['Normal']))
        
        # Build the PDF
        doc.build(story)
        
        logger.info(f"Generated PDF report: {output_path}")
        
    except Exception as e:
        logger.error(f"Error generating PDF report: {e}", exc_info=True)
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
                "description": "SQL injection vulnerability found in the search parameter. The application is vulnerable to boolean-based blind SQL injection attacks.",
                "impact": "An attacker could extract sensitive information from the database, modify database queries, or potentially gain unauthorized access to the system.",
                "remediation": "Use parameterized queries or prepared statements to prevent SQL injection. Input validation and output encoding should also be implemented.",
                "evidence": {
                    "request": "GET /search?q=test' OR '1'='1 HTTP/1.1\nHost: example.com\nUser-Agent: Mozilla/5.0\nAccept: text/html,application/xhtml+xml\n\n",
                    "response_code": 500,
                    "response_body_snippet": "Error: You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '1'' at line 1"
                },
                "references": [
                    "https://owasp.org/www-community/attacks/SQL_Injection",
                    "https://portswigger.net/web-security/sql-injection"
                ]
            },
            {
                "id": "vuln_002",
                "type": "XSS",
                "severity": "Medium",
                "url": "https://example.com/contact",
                "parameter": "message",
                "description": "Cross-site scripting (XSS) vulnerability found in the contact form. The application does not properly sanitize user input in the message parameter.",
                "impact": "An attacker could execute arbitrary JavaScript code in the context of the victim's browser, potentially leading to session hijacking, defacement, or redirection to malicious sites.",
                "remediation": "Implement proper input validation and output encoding. Use Content Security Policy (CSP) headers to mitigate the impact of XSS vulnerabilities.",
                "evidence": {
                    "request": "POST /contact HTTP/1.1\nHost: example.com\nContent-Type: application/x-www-form-urlencoded\n\nname=test&email=test@example.com&message=<script>alert('XSS')</script>",
                    "response_code": 200,
                    "response_body_snippet": "<div class=\"message\"><script>alert('XSS')</script></div>"
                },
                "references": [
                    "https://owasp.org/www-community/attacks/xss/",
                    "https://portswigger.net/web-security/cross-site-scripting"
                ]
            }
        ]
    }
    
    # Generate the report
    generate(example_results, "example_report.pdf", title="Example Security Report", version="1.0.0")
