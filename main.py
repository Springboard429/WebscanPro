import argparse, asyncio, json, sys
sys.path.insert(0, 'webscan')

from webscan.crawler import WebCrawler
from webscan.config import ScannerConfig

async def run_scan(url: str, config: ScannerConfig, output: str = None) -> dict:
    print(f"[*] Scanning: {url}")
    print(f"[*] Depth: {config.max_depth}, Concurrent: {config.max_concurrent}")

    async with WebCrawler(config) as crawler:
        result = await crawler.crawl(url)
        data = result.to_dict()
        data['statistics'] = crawler.get_stats()

        print(f"\n[+] Complete!")
        print(f"    URLs: {len(result.urls)}")
        print(f"    Forms: {len(result.forms)}")
        print(f"    Parameters: {len(result.parameters)}")
        print(f"    Logged in: {data['statistics'].get('logged_in', False)}")

        if output:
            with open(output, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"\n[+] Saved to: {output}")

        return data

def main():
    parser = argparse.ArgumentParser(description='WebScanPro - Target Scanning')
    parser.add_argument('--url', '-u', required=True, help='Target URL')
    parser.add_argument('--depth', '-d', type=int, default=3, help='Max depth (default: 3)')
    parser.add_argument('--concurrent', '-c', type=int, default=10, help='Concurrent requests (default: 10)')
    parser.add_argument('--timeout', '-t', type=int, default=30, help='Timeout (default: 30)')
    parser.add_argument('--output', '-o', help='Output JSON file')
    parser.add_argument('--login', action='store_true', help='Enable login')
    parser.add_argument('--login-url', help='Login page URL')
    parser.add_argument('--username', default='admin', help='Username')
    parser.add_argument('--password', default='password', help='Password')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    import logging
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                       format='%(levelname)s: %(message)s')

    config = ScannerConfig(
        max_depth=args.depth,
        max_concurrent=args.concurrent,
        request_timeout=args.timeout,
        login_url=args.login_url if args.login else None,
        login_username=args.username,
        login_password=args.password
    )

    if not args.url.startswith(('http://', 'https://')):
        args.url = 'http://' + args.url

    try:
        result = asyncio.run(run_scan(args.url, config, args.output))
        if not args.output:
            print(json.dumps(result, indent=2))
    except KeyboardInterrupt:
        print("\n[!] Interrupted")
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
