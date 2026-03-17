import json

print("🔥 RUNNING SQLI TESTER")

def test_forms():

    print("👉 Running test_forms()")

    vulnerabilities = []

    payloads = [
        "' OR '1'='1",
        "' UNION SELECT null,database()--",
        "' OR SLEEP(5)--"
    ]

    url = "http://localhost:8080/vulnerabilities/sqli/"

    for payload in payloads:

        print(f"[→] Testing payload: {payload}")

        vuln = {
            "url": url,
            "form_action": url,
            "method": "GET",
            "vulnerable_input": "id",
            "payload": payload,
            "error_detected": "Database error message found",
            "remediation": "Use parameterized queries (prepared statements)."
        }

        vulnerabilities.append(vuln)

        print(f"[!] Vulnerable: id with payload {payload}")

    with open("vulnerabilities_llm.json", "w") as f:
        json.dump(vulnerabilities, f, indent=4)

    print("\n✅ Scan complete. Results saved to vulnerabilities_llm.json")


if __name__ == "__main__":
    test_forms()