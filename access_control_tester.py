import requests
import json

BASE_URL = "http://localhost/"

# ---------- LOAD FORMS ----------
def load_forms():
    try:
        with open("forms.json", "r") as f:
            return json.load(f)
    except:
        print("forms.json not found")
        exit()


# ---------- BROKEN ACCESS CONTROL ----------
def test_broken_access():

    print("\n[+] Testing Broken Access Control...")

    forms = load_forms()
    vulnerabilities = []

    session = requests.Session()  # no login

    for form in forms:

        url = form["page"]

        # skip login page
        if "login.php" in url:
            continue

        try:
            response = session.get(url)

            # 🔥 if page is accessible without login
            if "login" not in response.text.lower():

                vuln = {
                    "type": "Broken Access Control",
                    "url": url,
                    "issue": "Accessible without authentication",
                    "remediation": "Restrict access using proper authentication checks."
                }

                vulnerabilities.append(vuln)

                print(f"[!] Public access detected: {url}")

        except:
            pass

    return vulnerabilities


# ---------- IDOR TEST ----------
def test_idor():

    print("\n[+] Testing IDOR...")

    forms = load_forms()
    vulnerabilities = []

    session = requests.Session()

    for form in forms:

        url = form["page"]
        method = form["method"]
        inputs = form["inputs"]

        for inp in inputs:

            name = inp.get("name")

            if not name:
                continue

            # 🔥 only test ID-like params
            if "id" in name.lower() or "user" in name.lower():

                print(f"\nTesting IDOR on {url} ({name})")

                try:
                    # baseline request
                    if method == "post":
                        r1 = session.post(url, data={name: "1"})
                        r2 = session.post(url, data={name: "2"})
                    else:
                        r1 = session.get(url, params={name: "1"})
                        r2 = session.get(url, params={name: "2"})

                    # 🔥 compare responses
                    if r1.text != r2.text:

                        vuln = {
                            "type": "IDOR",
                            "url": url,
                            "parameter": name,
                            "test_values": ["1", "2"],
                            "issue": "Direct object reference without authorization",
                            "remediation": "Validate user permissions for object access."
                        }

                        vulnerabilities.append(vuln)

                        print(f"[!] IDOR Found: {url} param={name}")

                except:
                    pass

    return vulnerabilities


# ---------- MAIN ----------
if __name__ == "__main__":

    all_vulns = []

    bac = test_broken_access()
    idor = test_idor()

    all_vulns.extend(bac)
    all_vulns.extend(idor)

    with open("access_vulnerabilities.json", "w") as f:
        json.dump(all_vulns, f, indent=4)

    print("\n[+] Scan complete → access_vulnerabilities.json")