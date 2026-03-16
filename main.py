#!/usr/bin/env python3
"""
WebScanPro - Advanced Web Application Security Scanner
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import local modules
try:
    from core.scan_controller import ScanController
    from core.crawler import WebCrawler
    from reports.report_generator import ReportGenerator
    from utils.logger import setup_logger
    from config import (
        SCAN_METHODS, REPORT_DIR, REPORT_FORMATS, LOG_LEVEL, LOG_FILE,
        LOG_FORMAT, LOG_MAX_SIZE, LOG_BACKUP_COUNT, BASE_DIR
    )
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure all required modules are in the correct location.")
    sys.exit(1)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='WebScanPro - Advanced Web Application Security Scanner',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Required arguments
    parser.add_argument(
        '-u', '--url',
        required=True,
        help='Target URL to scan'
    )
    
    # Scan options
    parser.add_argument(
        '--crawl-depth',
        type=int,
        default=2,
        help='Maximum depth to crawl'
    )
    parser.add_argument(
        '--threads',
        type=int,
        default=5,
        help='Number of concurrent threads to use'
    )
    
    # Authentication options
    parser.add_argument(
        '--username',
        type=str,
        help='Username for authentication (e.g., admin for DVWA)'
    )
    parser.add_argument(
        '--password',
        type=str,
        help='Password for authentication (e.g., password for DVWA)'
    )
    
    # Scan types
    parser.add_argument(
        '--scan-type',
        choices=['all', 'xss', 'sqli', 'idor', 'auth', 'access'],
        default='all',
        help='Type of scan to perform'
    )
    
    # Output options
    parser.add_argument(
        '-o', '--output',
        default='report',
        help='Output file name (without extension)'
    )
    parser.add_argument(
        '--format',
        choices=['html', 'pdf', 'json', 'all'],
        default='html',
        help='Output format'
    )
    parser.add_argument(
        '--no-external-apis',
        action='store_true',
        help='Disable external API lookups'
    )
    
    # Debugging
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )
    
    return parser.parse_args()

def setup_environment():
    """Set up the environment including logging and directories."""
    # Create necessary directories
    os.makedirs(REPORT_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    # Set up logging
    log_level = logging.DEBUG if '--debug' in sys.argv else LOG_LEVEL
    logger = setup_logger(
        'webscanpro',
        log_level=log_level
    )
    
    return logger

def main():
    """Main entry point for the WebScanPro application."""
    args = parse_arguments()
    logger = setup_environment()
    
    try:
        logger.info(f"Starting WebScanPro scan for {args.url}")
        logger.info(f"Scan type: {args.scan_type}")
        
        # Initialize components
        scanner = ScanController(
            target_url=args.url, 
            crawl_depth=args.crawl_depth,
            username=args.username,
            password=args.password
        )
        
        # Start the scan
        logger.info("Starting security scan...")
        scan_results = scanner.start_scan()
        
        # Generate reports
        logger.info("Generating reports...")
        report_gen = ReportGenerator(REPORT_DIR)
        
        if args.format in ['html', 'all']:
            html_report = report_gen.generate_report(scan_results, "html")
            report_path = os.path.join(REPORT_DIR, f"{args.output}.html")
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_report)
            logger.info(f"HTML report saved to {report_path}")
            
        if args.format in ['pdf', 'all']:
            pdf_report = report_gen.generate_report(scan_results, "pdf")
            report_path = os.path.join(REPORT_DIR, f"{args.output}.pdf")
            with open(report_path, 'wb') as f:
                f.write(pdf_report)
            logger.info(f"PDF report saved to {report_path}")
            
        if args.format in ['json', 'all']:
            json_report = report_gen.generate_report(scan_results, "json")
            report_path = os.path.join(REPORT_DIR, f"{args.output}.json")
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(json_report)
            logger.info(f"JSON report saved to {report_path}")
            # Output clean JSON to stdout for web interface
            if args.format == 'json':
                print(json_report)
            else:
                logger.info(f"JSON report: {json_report}")
            
        logger.info("Scan completed successfully!")
        
    except KeyboardInterrupt:
        logger.warning("Scan interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()









# #!/usr/bin/env python3
# """
# WebScanPro - Advanced Web Application Security Scanner

# A comprehensive security scanning tool for web applications that helps identify
# vulnerabilities and security issues.
# """

# import os
# import sys
# import argparse
# import logging
# from datetime import datetime
# from pathlib import Path

# # # Add the project root to the Python path
# # sys.path.insert(0, str(Path(__file__).parent.absolute()))

# # Add the project root to the Python path
# sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
 


# from core.scanner import WebScanner
# from core.crawler import WebCrawler
# from core.report_generator import ReportGenerator
# from utils.logger import setup_logger
# from config import (
#     SCAN_METHODS, REPORT_DIR, REPORT_FORMATS, LOG_LEVEL, LOG_FILE,
#     LOG_FORMAT, LOG_MAX_SIZE, LOG_BACKUP_COUNT, BASE_DIR
# )

# # Set up argument parser
# def parse_arguments():
#     """Parse command line arguments."""
#     parser = argparse.ArgumentParser(
#         description='WebScanPro - Advanced Web Application Security Scanner',
#         formatter_class=argparse.ArgumentDefaultsHelpFormatter
#     )
    
#     # Target options
#     target_group = parser.add_argument_group('Target')
#     target_group.add_argument(
#         '-u', '--url',
#         help='Target URL (e.g., https://example.com)',
#         required=True
#     )
#     target_group.add_argument(
#         '-f', '--file',
#         help='File containing a list of target URLs (one per line)'
#     )
#     target_group.add_argument(
#         '--crawl',
#         help='Enable crawling of the target website',
#         action='store_true'
#     )
#     target_group.add_argument(
#         '--max-depth',
#         type=int,
#         default=3,
#         help='Maximum depth to crawl'
#     )
#     target_group.add_argument(
#         '--max-pages',
#         type=int,
#         default=50,
#         help='Maximum number of pages to crawl'
#     )
    
#     # Scan options
#     scan_group = parser.add_argument_group('Scan Options')
#     scan_group.add_argument(
#         '--scan-type',
#         choices=['full', 'quick', 'custom'],
#         default='quick',
#         help='Type of scan to perform'
#     )
#     scan_group.add_argument(
#         '--scan-methods',
#         nargs='+',
#         choices=SCAN_METHODS.keys(),
#         help='Specific scan methods to run'
#     )
#     scan_group.add_argument(
#         '--exclude',
#         nargs='+',
#         choices=SCAN_METHODS.keys(),
#         help='Scan methods to exclude'
#     )
#     scan_group.add_argument(
#         '--threads',
#         type=int,
#         default=10,
#         help='Number of concurrent threads to use'
#     )
#     scan_group.add_argument(
#         '--rate-limit',
#         type=int,
#         default=10,
#         help='Maximum number of requests per second'
#     )
    
#     # Output options
#     output_group = parser.add_argument_group('Output')
#     output_group.add_argument(
#         '-o', '--output',
#         help='Output directory for reports',
#         default=REPORT_DIR
#     )
#     output_group.add_argument(
#         '--format',
#         nargs='+',
#         choices=REPORT_FORMATS,
#         default=['html'],
#         help='Output format(s) for the report'
#     )
#     output_group.add_argument(
#         '--no-report',
#         action='store_true',
#         help='Do not generate a report'
#     )
#     output_group.add_argument(
#         '-v', '--verbose',
#         action='count',
#         default=0,
#         help='Increase verbosity level (-v, -vv, -vvv)'
#     )
#     output_group.add_argument(
#         '--debug',
#         action='store_true',
#         help='Enable debug output'
#     )
    
#     # Authentication options
#     auth_group = parser.add_argument_group('Authentication')
#     auth_group.add_argument(
#         '--auth-type',
#         choices=['none', 'basic', 'form', 'bearer', 'ntlm', 'digest'],
#         default='none',
#         help='Authentication type'
#     )
#     auth_group.add_argument(
#         '--auth-url',
#         help='Authentication URL (for form-based auth)'
#     )
#     auth_group.add_argument(
#         '--username',
#         help='Username for authentication'
#     )
#     auth_group.add_argument(
#         '--password',
#         help='Password for authentication'
#     )
#     auth_group.add_argument(
#         '--token',
#         help='Bearer token for authentication'
#     )
#     auth_group.add_argument(
#         '--cookie',
#         help='Cookie string for authentication'
#     )
    
#     # Proxy options
#     proxy_group = parser.add_argument_group('Proxy')
#     proxy_group.add_argument(
#         '--proxy',
#         help='Proxy server (e.g., http://127.0.0.1:8080)'
#     )
#     proxy_group.add_argument(
#         '--proxy-cred',
#         help='Proxy credentials (username:password)'
#     )
    
#     # Advanced options
#     advanced_group = parser.add_argument_group('Advanced')
#     advanced_group.add_argument(
#         '--user-agent',
#         help='Custom User-Agent string'
#     )
#     advanced_group.add_argument(
#         '--timeout',
#         type=int,
#         default=10,
#         help='Request timeout in seconds'
#     )
#     advanced_group.add_argument(
#         '--retries',
#         type=int,
#         default=3,
#         help='Number of retries for failed requests'
#     )
#     advanced_group.add_argument(
#         '--delay',
#         type=float,
#         default=0,
#         help='Delay between requests in seconds'
#     )
#     advanced_group.add_argument(
#         '--verify-ssl',
#         action='store_true',
#         help='Verify SSL certificates'
#     )
#     advanced_group.add_argument(
#         '--follow-redirects',
#         action='store_true',
#         help='Follow HTTP redirects'
#     )
#     advanced_group.add_argument(
#         '--max-redirects',
#         type=int,
#         default=5,
#         help='Maximum number of redirects to follow'
#     )
    
#     # Version and help
#     parser.add_argument(
#         '--version',
#         action='version',
#         version='WebScanPro 1.0.0'
#     )
    
#     return parser.parse_args()

# def main():
#     """Main function."""
#     # Parse command line arguments
#     args = parse_arguments()
    
#     # Set up logging
#     log_level = logging.INFO
#     if args.debug:
#         log_level = logging.DEBUG
#     elif args.verbose >= 3:
#         log_level = logging.DEBUG
#     elif args.verbose == 2:
#         log_level = logging.INFO
#     elif args.verbose == 1:
#         log_level = logging.WARNING
    
#     logger = setup_logger('webscanpro', LOG_FILE, log_level, LOG_FORMAT, LOG_MAX_SIZE, LOG_BACKUP_COUNT)
    
#     # Log startup information
#     logger.info('=' * 70)
#     logger.info('WebScanPro - Advanced Web Application Security Scanner')
#     logger.info('=' * 70)
#     logger.info(f'Starting scan at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
#     logger.info(f'Command: {" ".join(sys.argv)}')
    
#     try:
#         # Initialize the scanner
#         scanner = WebScanner(
#             base_url=args.url,
#             scan_type=args.scan_type,
#             scan_methods=args.scan_methods,
#             exclude_methods=args.exclude,
#             threads=args.threads,
#             rate_limit=args.rate_limit,
#             output_dir=args.output,
#             report_formats=args.format,
#             auth_type=args.auth_type,
#             auth_url=args.auth_url,
#             username=args.username,
#             password=args.password,
#             token=args.token,
#             cookie=args.cookie,
#             proxy=args.proxy,
#             proxy_cred=args.proxy_cred,
#             user_agent=args.user_agent,
#             timeout=args.timeout,
#             retries=args.retries,
#             delay=args.delay,
#             verify_ssl=args.verify_ssl,
#             follow_redirects=args.follow_redirects,
#             max_redirects=args.max_redirects,
#             debug=args.debug
#         )
        
#         # Start the scan
#         scan_results = scanner.scan()
        
#         # Generate report if not disabled
#         if not args.no_report:
#             report_generator = ReportGenerator(scan_results, args.output)
#             report_paths = report_generator.generate_reports(args.format)
            
#             if report_paths:
#                 logger.info('Reports generated successfully:')
#                 for format, path in report_paths.items():
#                     logger.info(f'  - {format.upper()}: {path}')
        
#         logger.info('Scan completed successfully!')
#         return 0
    
#     except KeyboardInterrupt:
#         logger.warning('Scan interrupted by user')
#         return 130  # SIGINT
#     except Exception as e:
#         logger.error(f'An error occurred: {str(e)}', exc_info=args.debug)
#         return 1

# if __name__ == '__main__':
#     sys.exit(main())