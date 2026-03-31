import type { ScanKind, ScanRequest, ScanResponse } from './types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

export async function runScan(scanType: ScanKind, payload: ScanRequest): Promise<ScanResponse> {
  const response = await fetch(`${API_BASE_URL}/scan/${scanType}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  const data = await response.json().catch(() => null)

  if (!response.ok) {
    const detail = data?.detail || data?.error || `Request failed with status ${response.status}`
    throw new Error(detail)
  }

  return data as ScanResponse
}
