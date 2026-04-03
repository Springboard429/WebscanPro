from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import json
import os

app = FastAPI()

# allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- RUN SCAN ----------------
@app.get("/scan")
def run_scan():

    try:
        # run your main scanner
        subprocess.run(["python", "webscanpro.py"], check=True)

        return {"status": "Scan completed"}

    except Exception as e:
        return {"error": str(e)}


# ---------------- GET REPORT ----------------
@app.get("/report")
def get_report():

    if not os.path.exists("final_report.json"):
        return {"error": "Report not found"}

    with open("final_report.json", "r") as f:
        data = json.load(f)

    return data