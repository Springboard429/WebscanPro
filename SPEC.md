# WebScanPro FastAPI Backend - Specification

## Overview

FastAPI backend that exposes vulnerability scanning functionality via REST endpoints. Each endpoint first runs the crawler to discover URLs and forms, then executes the requested vulnerability module(s).

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   POST /scan/all       →  Crawler → SQli → XSS → AC/IDOR   │
│   POST /scan/sqli      →  Crawler → SQLi                    │
│   POST /scan/xss       →  Crawler → XSS                     │
│   POST /scan/access-control  →  Crawler → AC/IDOR           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  result.json    │  (shared crawler output)
                    └─────────────────┘
```

## Endpoints

### POST /scan/all

Runs the complete vulnerability scan pipeline.

**Request Body:**
```json
{
  "url": "http://localhost",
  "login_url": "http://localhost/login.php",
  "username": "admin",
  "password": "password"
}
```

**Response:**
```json
{
  "status": "completed",
  "crawler_stats": { "urls": 10, "forms": 5, "logged_in": true },
  "vulnerabilities": {
    "sql_injection": [...],
    "xss": [...],
    "access_control": [...]
  },
  "total_vulnerabilities": 3
}
```

### POST /scan/sqli

Runs crawler + SQL injection testing only.

**Request Body:** Same as `/scan/all`

**Response:**
```json
{
  "status": "completed",
  "crawler_stats": { "urls": 10, "forms": 5, "logged_in": true },
  "vulnerabilities": {
    "sql_injection": [...]
  }
}
```

### POST /scan/xss

Runs crawler + XSS testing only.

**Request Body:** Same as `/scan/all`

**Response:**
```json
{
  "status": "completed",
  "crawler_stats": { "urls": 10, "forms": 5, "logged_in": true },
  "vulnerabilities": {
    "xss": [...]
  }
}
```

### POST /scan/access-control

Runs crawler + Access Control/IDOR testing only.

**Request Body:** Same as `/scan/all`

**Response:**
```json
{
  "status": "completed",
  "crawler_stats": { "urls": 10, "forms": 5, "logged_in": true },
  "vulnerabilities": {
    "access_control": [...]
  }
}
```

### GET /scan/{scan_id}

Retrieve results of a previously started scan (future enhancement for async).

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

## Data Models

### ScanRequest
| Field      | Type   | Required | Default   | Description           |
|------------|--------|----------|-----------|-----------------------|
| url        | string | Yes      | -         | Target base URL       |
| login_url  | string | No       | null      | Login page URL        |
| username   | string | No       | "admin"   | Login username        |
| password   | string | No       | "password"| Login password        |

### ScanResponse
| Field             | Type   | Description                              |
|-------------------|--------|------------------------------------------|
| status            | string | "completed", "failed", "running"        |
| crawler_stats     | dict   | Statistics from crawler run              |
| vulnerabilities   | dict   | Nested dict of vulnerability findings    |
| total_vulnerabilities | int | Count of all vulnerabilities found       |

### VulnerabilityFinding
| Field           | Type   | Description                     |
|-----------------|--------|---------------------------------|
| url             | string | Affected URL                    |
| vulnerability_type | string | Type (SQLi, XSS, IDOR, BAC)   |
| vulnerable_input | string | Input field name               |
| payload         | string | Exploit payload used           |
| remediation      | string | Fix recommendation             |

## Workflow

1. **Request received** → Validate input (URL format, etc.)
2. **Run crawler** → Execute `main.py` with `--url`, `--login-url`, `--login` flags, output to `result.json`
3. **Load crawler output** → Read `result.json` into memory
4. **Run vulnerability module(s)** → Execute respective module script(s) using the shared `result.json`
5. **Aggregate results** → Combine crawler stats + vulnerability findings
6. **Return response** → JSON response with all findings

## File Structure

```
webscanpro/
├── api/
│   ├── __init__.py
│   ├── main.py           # FastAPI app entry point
│   ├── routes/
│   │   ├── __init__.py
│   │   └── scan.py       # /scan endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py    # Pydantic models
│   └── services/
│       ├── __init__.py
│       ├── crawler.py    # Crawler execution logic
│       └── tester.py     # Module execution logic
├── modules/
│   ├── sqli_tester.py
│   ├── xss_tester.py
│   └── access_control_tester.py
├── main.py               # Existing CLI crawler
├── webscanpro.py         # Existing pipeline
└── SPEC.md
```

## Configuration

- Crawler settings (depth, concurrency, timeout) use sensible defaults from `ScannerConfig`
- LLM settings (Ollama) read from environment variables
- No database required - results returned directly in response

## Error Handling

- Invalid URL format → 422 Unprocessable Entity
- Crawler failure → 500 Internal Server Error with error details
- Module execution failure → Partial results returned with error field
- Timeout handling → Configurable via request_timeout

## Dependencies

- fastapi
- uvicorn
- pydantic
- httpx (async HTTP client)
- All existing dependencies (requests, beautifulsoup4, openai, etc.)
