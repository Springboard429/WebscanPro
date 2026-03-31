# WebScanPro Frontend

React + TypeScript UI for the FastAPI backend in this repository.

## Features

- Trigger scans for all modules or one module at a time.
- Submit target URL plus optional login credentials.
- View crawler stats and grouped vulnerability findings.
- Configure backend URL via environment variable.

## Run Locally

1. Install dependencies:

   ```bash
   npm install
   ```

2. Configure API base URL:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` if your API is not running at `http://127.0.0.1:8000`.

3. Start development server:

   ```bash
   npm run dev
   ```

## Production Build

```bash
npm run build
```
