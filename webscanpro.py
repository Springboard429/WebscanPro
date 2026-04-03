from crawler import *
from sqli_tester import test_forms as test_sqli
from sqli_llm_tester import test_forms as test_sqli_llm
from xss_tester import test_xss
from xss_tester_llm import test_forms as test_xss_llm
from report_generator import generate_final_json, generate_html


def run_all():

    print("\n🚀 Starting Full WebScanPro Scan...\n")

    # Step 1: Crawl
    login()
    print("✔ Crawling completed")

    # Step 2: SQL Injection
    test_sqli()
    print("✔ SQL Injection scan done")

    test_sqli_llm()
    print("✔ LLM SQL scan done")

    # Step 3: XSS
    test_xss()
    print("✔ XSS scan done")

    test_xss_llm()
    print("✔ LLM XSS scan done")

    # Step 4: Report
    data = generate_final_json()
    generate_html(data)

    print("\n✅ FULL SCAN COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    run_all()