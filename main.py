from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.scan import router as scan_router

app = FastAPI(title="WebScanPro API")

# ✅ ADD THIS BLOCK
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow frontend
    allow_credentials=True,
    allow_methods=["*"],   # allow POST, OPTIONS etc
    allow_headers=["*"],
)

app.include_router(scan_router)

@app.get("/")
def home():
    return {"message": "WebScanPro API running"}