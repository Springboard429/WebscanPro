import json
import os
import html

def safe(value):
    return html.escape(str(value))

# ---------------- FILES ----------------
FILES = {
    "SQL Injection": [
        "vulnerabilities.json",
        "vulnerabilities_llm.json"
    ],
    "XSS": [
        "xss_vulnerabilities.json",
        "xss_vulnerabilities_llm.json"
    ],
    "Access Control / IDOR": [
        "access_vulnerabilities.json"
    ]
}


# ---------------- LOAD FILE ----------------
def load_file(file):
    if not os.path.exists(file):
        return []

    try:
        with open(file, "r") as f:
            data = json.load(f)

            # if empty or invalid
            if not isinstance(data, list):
                return []

            return data

    except:
        return []


# ---------------- GENERATE FINAL JSON ----------------
def generate_final_json():

    final_report = {
        "summary": {
            "total_vulnerabilities": 0,
            "SQL Injection": 0,
            "XSS": 0,
            "Access Control / IDOR": 0
        },
        "details": {}
    }

    for category, file_list in FILES.items():

        final_report["details"][category] = []

        for file in file_list:

            data = load_file(file)

            final_report["details"][category].extend(data)

        count = len(final_report["details"][category])

        final_report["summary"][category] = count
        final_report["summary"]["total_vulnerabilities"] += count

    # save JSON
    with open("final_report.json", "w") as f:
        json.dump(final_report, f, indent=4)

    print("[+] final_report.json created")

    return final_report


# ---------------- GENERATE HTML ----------------
def generate_html(data):

    html_content = """
    <html>
    <head>
        <title>WebScanPro Report</title>
        <style>
            body { font-family: Arial; background: #f4f4f4; padding: 20px; }
            h1 { text-align: center; }
            .summary { background: white; padding: 15px; border-radius: 10px; margin-bottom: 20px; }
            .section { background: white; padding: 15px; border-radius: 10px; margin-bottom: 20px; }
            .vuln { margin: 10px 0; padding: 10px; border-left: 5px solid red; background: #ffe6e6; word-wrap: break-word; }
        </style>
    </head>
    <body>

    <h1>WebScanPro - Vulnerability Report</h1>
    """

    # ---------- SUMMARY ----------
    summary = data["summary"]

    html_content += "<div class='summary'>"
    html_content += f"<p><b>Total Vulnerabilities:</b> {summary['total_vulnerabilities']}</p>"
    html_content += f"<p>SQL Injection: {summary['SQL Injection']}</p>"
    html_content += f"<p>XSS: {summary['XSS']}</p>"
    html_content += f"<p>Access Control / IDOR: {summary['Access Control / IDOR']}</p>"
    html_content += "</div>"

    # ---------- DETAILS ----------
    for category, vulns in data["details"].items():

        html_content += f"<div class='section'><h2>{safe(category)}</h2>"

        if not vulns:
            html_content += "<p>No vulnerabilities found</p>"

        for v in vulns:
            html_content += "<div class='vuln'>"

            for key, value in v.items():
                html_content += f"<b>{safe(key)}:</b> {safe(value)}<br>"

            html_content += "</div>"

        html_content += "</div>"

    html_content += "</body></html>"

    # save HTML
    with open("final_report.html", "w") as f:
        f.write(html_content)

    print("[+] final_report.html created")


# ---------------- MAIN ----------------
if __name__ == "__main__":

    data = generate_final_json()
    generate_html(data)