from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from enum import Enum


class VulnerabilityType(str, Enum):
    SQLI = "sql_injection"
    XSS = "xss"
    ACCESS_CONTROL = "access_control"


class ScanRequest(BaseModel):
    url: str = Field(..., description="Target base URL", examples=["http://localhost"])
    login_url: Optional[str] = Field(None, description="Login page URL", examples=["http://localhost/login.php"])
    username: str = Field("admin", description="Login username")
    password: str = Field("password", description="Login password")


class VulnerabilityFinding(BaseModel):
    url: str
    vulnerability_type: str
    description: Optional[str] = None
    vulnerable_input: Optional[str] = None
    payload: Optional[str] = None
    error_detected: Optional[str] = None
    remediation: Optional[str] = None


class CrawlerStats(BaseModel):
    urls: int = 0
    forms: int = 0
    parameters: int = 0
    logged_in: bool = False


class ScanResponse(BaseModel):
    status: str = Field(..., description="completed, failed, or running")
    crawler_stats: Optional[CrawlerStats] = None
    vulnerabilities: dict = Field(default_factory=dict)
    total_vulnerabilities: int = 0
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"
