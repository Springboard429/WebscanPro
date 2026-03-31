export type ScanKind = 'all' | 'sqli' | 'xss' | 'access-control'

export type ScanRequest = {
  url: string
  login_url?: string
  username: string
  password: string
}

export type VulnerabilityFinding = {
  url: string
  vulnerability_type?: string
  description?: string
  vulnerable_input?: string
  payload?: string
  error_detected?: string
  remediation?: string
}

export type CrawlerStats = {
  urls: number
  forms: number
  parameters: number
  logged_in: boolean
}

export type ScanResponse = {
  status: string
  crawler_stats?: CrawlerStats
  vulnerabilities: Record<string, VulnerabilityFinding[]>
  total_vulnerabilities: number
  error?: string
}
