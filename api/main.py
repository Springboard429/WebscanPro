from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .models.schemas import HealthResponse
from .routes.scan import router as scan_router

app = FastAPI(
    title="WebScanPro API",
    description="AI-driven web vulnerability scanner backend",
    version="1.0.0",
)

allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scan_router)


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="healthy")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
