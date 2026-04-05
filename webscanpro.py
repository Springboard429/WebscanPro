BASE_URL = "http://localhost/"
LOGIN_URL = BASE_URL + "login.php"
from report_generator import generate_final_json, generate_html


def run_all():

    print("\n🚀 Starting Full WebScanPro Scan...\n")

    # Step 1: Crawl
    print("🔄 Running crawler...")
    import crawler   # this will execute crawler script
    print("✔ Crawling completed")

    # Step 2: SQL Injection
    import sqli_tester
    print("✔ SQL Injection scan done")

    import sqli_llm_tester
    print("✔ LLM SQL scan done")

    # Step 3: XSS
    import xss_tester
    print("✔ XSS scan done")

    import xss_tester_llm
    print("✔ LLM XSS scan done")

    import access_control_tester
    print("✔ Access Control scan done")
    
    # Step 4: Report
    data = generate_final_json()
    generate_html(data)

    print("\n✅ FULL SCAN COMPLETED SUCCESSFULLY")


# 🔥 THIS LINE WAS MISSING
if __name__ == "__main__":
    run_all()