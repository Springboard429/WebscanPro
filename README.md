# WebScanPro

A full-stack web vulnerability scanner application with an AI-driven backend API and a React-based frontend dashboard.

## Architecture

- **Backend**: FastAPI + Python subprocesses for crawler and security testers (SQLi, XSS, Access Control)
- **Frontend**: React 18 + TypeScript + Vite + CSS-in-JS

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- curl or Postman (for testing API endpoints)

---

## Backend Setup

### 1. Create Virtual Environment

```bash
cd /path/to/webscanpro
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Verify installation:
```bash
python -c "import aiohttp, fastapi; print('Dependencies OK')"
```

### 3. Run FastAPI Server

```bash
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**API is now live** at `http://127.0.0.1:8000`.

Test health endpoint:
```bash
curl http://127.0.0.1:8000/health
```

Expected response:
```json
{"status":"healthy","version":"1.0.0"}
```

---

## Frontend Setup

### 1. Navigate to Frontend Directory

```bash
cd frontend
```

### 2. Install Node Dependencies

```bash
npm install
```

### 3. Configure Backend URL (Optional)

Create `.env` from the example if you need to change the API base URL:

```bash
cp .env.example .env
```

Edit `.env` if your backend is not running on `http://127.0.0.1:8000`:
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

### 4. Run Development Server

```bash
npm run dev
```

You should see:
```
  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

**Frontend is now live** at `http://localhost:5173`.

---

## Development Workflow

### Terminal 1: Backend

```bash
cd /path/to/webscanpro
source .venv/bin/activate
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

### Terminal 2: Frontend

```bash
cd /path/to/webscanpro/frontend
npm run dev
```

### Terminal 3: Optional — Run Tests

```bash
# From root directory, activate venv
source .venv/bin/activate

# Run individual scanner modules manually
python modules/sqli_tester.py <url> <login_url> result.json
python modules/xss_tester.py <url> <login_url> result.json
python modules/access_control_tester.py <url> <login_url> result.json
```

---

## API Endpoints

All requests require JSON body with:
```json
{
  "url": "http://target.com",
  "login_url": "http://target.com/login.php",
  "username": "admin",
  "password": "password"
}
```

### Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Liveness check |
| POST | `/scan/all` | Run all scanners (crawler + SQLi + XSS + Access Control) |
| POST | `/scan/sqli` | Run SQL injection tester only |
| POST | `/scan/xss` | Run XSS tester only |
| POST | `/scan/access-control` | Run IDOR/privilege checker only |

### Example cURL Request

```bash
curl -X POST http://127.0.0.1:8000/scan/all \
  -H "Content-Type: application/json" \
  -d '{
    "url": "http://testphp.vulnweb.com",
    "login_url": "",
    "username": "admin",
    "password": "password"
  }'
```

### Example Response

```json
{
  "status": "completed",
  "crawler_stats": {
    "urls": 42,
    "forms": 8,
    "parameters": 15,
    "logged_in": false
  },
  "vulnerabilities": {
    "sql_injection": [...],
    "xss": [...],
    "access_control": [...]
  },
  "total_vulnerabilities": 47,
  "error": null
}
```

---

## Project Structure

```
webscanpro/
├── api/                          # FastAPI backend
│   ├── main.py                   # FastAPI app + CORS middleware
│   ├── models/schemas.py         # Pydantic request/response models
│   ├── routes/scan.py            # Scan endpoints
│   └── services/
│       ├── crawler.py            # Run crawler subprocess
│       └── tester.py             # Run scanner subprocesses
├── frontend/                     # React + TypeScript UI
│   ├── src/
│   │   ├── App.tsx              # Main UI component
│   │   ├── App.css              # Page styling
│   │   ├── api.ts               # API client
│   │   └── types.ts             # TypeScript types
│   ├── package.json
│   ├── .env.example
│   └── vite.config.ts
├── webscan/                      # Crawler module
│   ├── crawler.py               # WebCrawler class
│   └── ...
├── modules/                      # Security testers
│   ├── sqli_tester.py           # SQL injection checks
│   ├── xss_tester.py            # XSS checks
│   └── access_control_tester.py # IDOR/ACL checks
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## Troubleshooting

### Backend Issues

**ModuleNotFoundError: No module named 'aiohttp'**
- Make sure you activated the virtual environment: `source .venv/bin/activate`
- Reinstall requirements: `pip install -r requirements.txt`
- Ensure you're using the correct Python: `.venv/bin/python --version`

**CORS error in frontend**
- Backend must be running on `http://127.0.0.1:8000`
- Frontend is at `http://localhost:5173`
- Both are configured in the CORS middleware in [api/main.py](api/main.py)
- Restart uvicorn after any CORS config changes

**Crawler fails with "Crawler failed" error**
- Check that the target URL is reachable
- Increase `--timeout` value if the target is slow
- Try with a public test site like `http://testphp.vulnweb.com`

### Frontend Issues

**npm install fails**
- Clear npm cache: `npm cache clean --force`
- Remove node_modules: `rm -rf node_modules package-lock.json`
- Reinstall: `npm install`

**Frontend can't reach backend**
- Verify backend is running: `curl http://127.0.0.1:8000/health`
- Check `VITE_API_BASE_URL` in frontend `.env`
- Check browser console (F12) for exact error message

**Port already in use**
- Backend port 8000: `lsof -i :8000` to find PID, then `kill -9 <PID>`
- Frontend port 5173: `lsof -i :5173` to find PID, then `kill -9 <PID>`

---

## Production Build

### Frontend

```bash
cd frontend
npm run build
```

Outputs optimized bundle to `frontend/dist/`.

Deploy to static host (Vercel, Netlify, AWS S3, etc.):
```bash
npm run build && npx vercel --prod
```

### Backend

Run with Uvicorn for production:
```bash
uvicorn api.main:app --reload
```

Or with Docker:
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Environment Variables

Create a `.env` file in the root for backend config (optional):

```env
# Backend settings (if needed in future)
API_HOST=127.0.0.1
API_PORT=8000
DEBUG=True
```

Frontend `.env` (in `frontend/` folder):
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

---

## Testing the Scanner

Use a vulnerable test site:
- **DVWA** (Damn Vulnerable Web App): http://testphp.vulnweb.com
- **WebGoat**: Running locally or Docker
- **OWASP Juice Shop**: https://juice-shop.herokuapp.com/

Example scan request via UI:
1. Open http://localhost:5173
2. Select "Full Scan"
3. Enter URL: `http://testphp.vulnweb.com`
4. Leave login URL empty (or provide if needed)
5. Click "Run Scan"
6. View results in dashboard

---

## Contributing

- Backend changes: Restart uvicorn (`--reload` watches for changes)
- Frontend changes: Vite hot module replacement (HMR) auto-refreshes browser
- Add new scanner types in `modules/` folder and wire them in [api/routes/scan.py](api/routes/scan.py)

---

## License

MIT

---

## Questions?

Check [frontend/README.md](frontend/README.md) for frontend-specific docs.
Check [api/main.py](api/main.py) for API configuration.
