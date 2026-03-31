import { useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import { runScan } from './api'
import type { ScanKind, ScanRequest, ScanResponse, VulnerabilityFinding } from './types'
import './App.css'

const SCAN_OPTIONS: Array<{ label: string; value: ScanKind; description: string }> = [
  { label: 'Full Scan', value: 'all', description: 'Crawler + SQLi + XSS + Access Control' },
  { label: 'SQL Injection', value: 'sqli', description: 'Run focused SQLi checks only' },
  { label: 'Cross-Site Scripting', value: 'xss', description: 'Run reflected/stored XSS checks' },
  { label: 'Access Control', value: 'access-control', description: 'Run IDOR and privilege checks' },
]

const defaultForm: ScanRequest = {
  url: '',
  login_url: '',
  username: 'admin',
  password: 'password',
}

function App() {
  const [scanType, setScanType] = useState<ScanKind>('all')
  const [form, setForm] = useState<ScanRequest>(defaultForm)
  const [result, setResult] = useState<ScanResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isScanning, setIsScanning] = useState(false)

  const totalByType = useMemo(() => {
    if (!result?.vulnerabilities) {
      return []
    }

    return Object.entries(result.vulnerabilities).map(([key, findings]) => ({
      key,
      total: findings.length,
    }))
  }, [result])

  const submitScan = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError(null)
    setResult(null)
    setIsScanning(true)

    try {
      const payload: ScanRequest = {
        ...form,
        login_url: form.login_url?.trim() || undefined,
      }
      const scanResult = await runScan(scanType, payload)
      setResult(scanResult)
    } catch (scanError) {
      if (scanError instanceof Error) {
        setError(scanError.message)
      } else {
        setError('Unexpected error while running scan.')
      }
    } finally {
      setIsScanning(false)
    }
  }

  const total = result?.total_vulnerabilities ?? 0
  const status = result?.status ?? 'idle'

  return (
    <main className="shell">
      <div className="background-grid" aria-hidden="true" />
      <section className="hero-panel">
        <p className="kicker">WebScanPro Frontend</p>
        <h1>Vulnerability Scans With One Control Center</h1>
        <p className="hero-copy">
          Trigger scanner jobs, monitor crawler statistics, and inspect findings from your FastAPI backend in a single interface.
        </p>
      </section>

      <section className="content-layout">
        <form className="scan-form" onSubmit={submitScan}>
          <h2>Start A Scan</h2>

          <div className="field">
            <label htmlFor="scanType">Scan Type</label>
            <select
              id="scanType"
              value={scanType}
              onChange={(event) => setScanType(event.target.value as ScanKind)}
              disabled={isScanning}
            >
              {SCAN_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <p className="inline-help">
              {SCAN_OPTIONS.find((option) => option.value === scanType)?.description}
            </p>
          </div>

          <div className="field">
            <label htmlFor="targetUrl">Target URL</label>
            <input
              id="targetUrl"
              type="url"
              placeholder="http://testphp.vulnweb.com"
              value={form.url}
              onChange={(event) => setForm((prev) => ({ ...prev, url: event.target.value }))}
              required
              disabled={isScanning}
            />
          </div>

          <div className="field">
            <label htmlFor="loginUrl">Login URL (Optional)</label>
            <input
              id="loginUrl"
              type="url"
              placeholder="http://testphp.vulnweb.com/login.php"
              value={form.login_url ?? ''}
              onChange={(event) => setForm((prev) => ({ ...prev, login_url: event.target.value }))}
              disabled={isScanning}
            />
          </div>

          <div className="split-row">
            <div className="field">
              <label htmlFor="username">Username</label>
              <input
                id="username"
                type="text"
                value={form.username}
                onChange={(event) => setForm((prev) => ({ ...prev, username: event.target.value }))}
                disabled={isScanning}
              />
            </div>
            <div className="field">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                value={form.password}
                onChange={(event) => setForm((prev) => ({ ...prev, password: event.target.value }))}
                disabled={isScanning}
              />
            </div>
          </div>

          <button type="submit" disabled={isScanning || !form.url.trim()}>
            {isScanning ? 'Scanning...' : 'Run Scan'}
          </button>
        </form>

        <section className="results-panel" aria-live="polite">
          <header>
            <h2>Result Dashboard</h2>
            <span className={`status-pill ${status}`}>{status.toUpperCase()}</span>
          </header>

          {error && <p className="error-banner">{error}</p>}

          {!error && !result && !isScanning && (
            <p className="empty-state">
              No scan has run yet. Submit the form to fetch vulnerabilities from the backend.
            </p>
          )}

          {isScanning && (
            <p className="loading-state">Executing scanner modules. This may take a minute...</p>
          )}

          {result && (
            <>
              <div className="summary-grid">
                <article>
                  <h3>Total Findings</h3>
                  <p>{total}</p>
                </article>
                <article>
                  <h3>URLs Crawled</h3>
                  <p>{result.crawler_stats?.urls ?? 0}</p>
                </article>
                <article>
                  <h3>Forms Seen</h3>
                  <p>{result.crawler_stats?.forms ?? 0}</p>
                </article>
                <article>
                  <h3>Auth State</h3>
                  <p>{result.crawler_stats?.logged_in ? 'Logged In' : 'Anonymous'}</p>
                </article>
              </div>

              <div className="type-grid">
                {totalByType.length === 0 && <p>No vulnerability groups returned.</p>}
                {totalByType.map((entry) => (
                  <div key={entry.key} className="type-chip">
                    <span>{entry.key.replace('_', ' ')}</span>
                    <strong>{entry.total}</strong>
                  </div>
                ))}
              </div>

              <div className="findings-list">
                {Object.entries(result.vulnerabilities).map(([group, findings]) => (
                  <section key={group} className="finding-group">
                    <h3>{group.replace('_', ' ').toUpperCase()}</h3>
                    {findings.length === 0 && <p className="none-found">No findings in this category.</p>}
                    {findings.map((finding, index) => (
                      <article key={`${group}-${index}`}>
                        <p className="finding-url">{(finding as VulnerabilityFinding).url || 'Unknown URL'}</p>
                        <p>{(finding as VulnerabilityFinding).description || 'No description provided.'}</p>
                        {(finding as VulnerabilityFinding).payload && (
                          <pre>{(finding as VulnerabilityFinding).payload}</pre>
                        )}
                      </article>
                    ))}
                  </section>
                ))}
              </div>
            </>
          )}
        </section>
      </section>
    </main>
  )
}

export default App
