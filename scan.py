from fastapi import APIRouter
import subprocess
import sys
import json
from pdf_report_generator import generate_pdf
from fastapi.responses import FileResponse

router = APIRouter(prefix="/scan", tags=["Scan"])


# 🔥 FULL SCAN (like your sir UI)
@router.post("/all")
def full_scan():

    try:
        print("[+] Running full pipeline...")

        # Step 1: Crawl
        subprocess.run([sys.executable, "crawl.py"], check=True)

        # Step 2: SQLi (LLM)
        subprocess.run([sys.executable, "sqli_tester_ollama.py"], check=True)

        # Step 3: XSS (LLM)
        subprocess.run([sys.executable, "xss_tester_ollama.py"], check=True)

        # Step 4: Access Control
        subprocess.run([sys.executable, "access_control_tester.py"], check=True)

        # Step 5: Final JSON
        subprocess.run([sys.executable, "final_report_generator.py"], check=True)

        with open("final_report.json", "r") as f:
            report = json.load(f)

        return {
            "status": "success",
            "report": report
        }

    except Exception as e:
        return {"error": str(e)}


# 🔹 Individual APIs
@router.post("/sqli")
def sqli_scan():
    subprocess.run([sys.executable, "sqli_tester_ollama.py"])
    return json.load(open("vulnerabilities_llm.json"))


@router.post("/xss")
def xss_scan():
    subprocess.run([sys.executable, "xss_tester_ollama.py"])
    return json.load(open("xss_vulnerabilities_llm.json"))


@router.post("/access-control")
def access_scan():
    subprocess.run([sys.executable, "access_control_tester.py"])
    return json.load(open("access_control_vulnerabilities.json"))

@router.get("/download-report")
def download_report():
    file_path = "final_report.html"

    return FileResponse(
        path=file_path,
        filename="webscan_report.html",
        media_type="text/html"
    )