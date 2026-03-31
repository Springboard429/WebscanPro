from fastapi import APIRouter, HTTPException

from ..models.schemas import ScanRequest, ScanResponse, CrawlerStats
from ..services import crawler, tester

router = APIRouter(prefix="/scan", tags=["scan"])


def _build_stats(crawler_data: dict) -> CrawlerStats:
    stats = crawler_data.get("statistics", {})
    return CrawlerStats(
        urls=len(crawler_data.get("urls", [])),
        forms=len(crawler_data.get("forms", [])),
        parameters=len(crawler_data.get("parameters", [])),
        logged_in=stats.get("logged_in", False),
    )


@router.post("/all", response_model=ScanResponse)
async def scan_all(request: ScanRequest):
    try:
        crawler_data = await crawler.run_crawler(
            url=request.url,
            login_url=request.login_url,
            username=request.username,
            password=request.password,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crawler failed: {str(e)}")

    sqli_vulns, xss_vulns, ac_vulns = [], [], []

    try:
        sqli_vulns = await tester.run_sqli_tester(request.url, request.login_url)
    except Exception:
        pass

    try:
        xss_vulns = await tester.run_xss_tester(request.url, request.login_url)
    except Exception:
        pass

    try:
        ac_vulns = await tester.run_access_control_tester(request.url, request.login_url)
    except Exception:
        pass

    total = len(sqli_vulns) + len(xss_vulns) + len(ac_vulns)
    return ScanResponse(
        status="completed",
        crawler_stats=_build_stats(crawler_data),
        vulnerabilities={
            "sql_injection": sqli_vulns,
            "xss": xss_vulns,
            "access_control": ac_vulns,
        },
        total_vulnerabilities=total,
    )


@router.post("/sqli", response_model=ScanResponse)
async def scan_sqli(request: ScanRequest):
    try:
        crawler_data = await crawler.run_crawler(
            url=request.url,
            login_url=request.login_url,
            username=request.username,
            password=request.password,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crawler failed: {str(e)}")

    sqli_vulns = []
    try:
        sqli_vulns = await tester.run_sqli_tester(request.url, request.login_url)
    except Exception as e:
        return ScanResponse(
            status="failed",
            crawler_stats=_build_stats(crawler_data),
            error=str(e),
        )

    return ScanResponse(
        status="completed",
        crawler_stats=_build_stats(crawler_data),
        vulnerabilities={"sql_injection": sqli_vulns},
        total_vulnerabilities=len(sqli_vulns),
    )


@router.post("/xss", response_model=ScanResponse)
async def scan_xss(request: ScanRequest):
    try:
        crawler_data = await crawler.run_crawler(
            url=request.url,
            login_url=request.login_url,
            username=request.username,
            password=request.password,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crawler failed: {str(e)}")

    xss_vulns = []
    try:
        xss_vulns = await tester.run_xss_tester(request.url, request.login_url)
    except Exception as e:
        return ScanResponse(
            status="failed",
            crawler_stats=_build_stats(crawler_data),
            error=str(e),
        )

    return ScanResponse(
        status="completed",
        crawler_stats=_build_stats(crawler_data),
        vulnerabilities={"xss": xss_vulns},
        total_vulnerabilities=len(xss_vulns),
    )


@router.post("/access-control", response_model=ScanResponse)
async def scan_access_control(request: ScanRequest):
    try:
        crawler_data = await crawler.run_crawler(
            url=request.url,
            login_url=request.login_url,
            username=request.username,
            password=request.password,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crawler failed: {str(e)}")

    ac_vulns = []
    try:
        ac_vulns = await tester.run_access_control_tester(request.url, request.login_url)
    except Exception as e:
        return ScanResponse(
            status="failed",
            crawler_stats=_build_stats(crawler_data),
            error=str(e),
        )

    return ScanResponse(
        status="completed",
        crawler_stats=_build_stats(crawler_data),
        vulnerabilities={"access_control": ac_vulns},
        total_vulnerabilities=len(ac_vulns),
    )
