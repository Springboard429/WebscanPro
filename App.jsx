import { useState } from "react";
import "./App.css";

function App() {
  const [selectedType,setSelectedType]=useState(null);
  const [scanType, setScanType] = useState("all");
  const [targetUrl, setTargetUrl] = useState("");
  const [loginUrl, setLoginUrl] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

const runScan = async () => {
  setLoading(true);

  let endpoint = "";

  if (scanType === "all") endpoint = "scan/all";
  else if (scanType === "sqli") endpoint = "scan/sqli";
  else if (scanType === "xss") endpoint = "scan/xss";
  else if (scanType === "access-control") endpoint = "scan/access-control";

  const res = await fetch(`http://127.0.0.1:8000/${endpoint}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      url: targetUrl,
      login_url: loginUrl,
      username,
      password
    })
  });

  const result = await res.json();

  // FULL scan returns report
  if (scanType === "all") {
    setData(result.report);
  } else {
    // single scan → wrap it like full structure
    setData({
      total_vulnerabilities: result.length,
      vulnerabilities: {
        sql_injection: scanType === "sqli" ? result : [],
        cross_site_scripting: scanType === "xss" ? result : [],
        access_control_and_idor: scanType === "access-control" ? result : []
      }
    });
  }

  setLoading(false);
};

  return (
    <div className="main">
    <div className="header">
      <h1>🛡️ WebScanPro</h1>
      <p>Automated Web Vulnerabilty Scanner Dashboard</p>

      <div className="container">

        {/* LEFT FORM */}
        <div className="form-box">
          <h2>Start Scan</h2>
          <select
  value={scanType}
  onChange={(e) => setScanType(e.target.value)}
>
  <option value="all">Full Scan</option>
  <option value="sqli">SQL Injection</option>
  <option value="xss">XSS</option>
  <option value="access-control">Access Control</option>
</select>

          <input
            placeholder="Target URL"
            value={targetUrl}
            onChange={(e) => setTargetUrl(e.target.value)}
          />

          <input
            placeholder="Login URL"
            value={loginUrl}
            onChange={(e) => setLoginUrl(e.target.value)}
          />

          <input
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <button onClick={runScan}>
            {loading ? "Scanning..." : "Run Scan"}
          </button>
        </div>

        {/* RIGHT DASHBOARD */}
        <div className="dashboard">

          {!data && <p>No scan yet</p>}

          {data && (
            <>
              <h2>Total: {data.total_vulnerabilities}</h2>

              <div className="cards">
              <div className="card red" onClick={() => setSelectedType("sql_injection")}>
  SQLi: {data.vulnerabilities.sql_injection.length}
</div>

<div className="card orange" onClick={() => setSelectedType("cross_site_scripting")}>
  XSS: {data.vulnerabilities.cross_site_scripting.length}
</div>

<div className="card green" onClick={() => setSelectedType("access_control_and_idor")}>
  Access: {data.vulnerabilities.access_control_and_idor.length}
</div>
              </div>
               <button
      onClick={() => window.open("http://127.0.0.1:8000/scan/download-report")}
      style={{
        marginTop: "20px",
        padding: "10px 20px",
        background: "#38bdf8",
        border: "none",
        borderRadius: "8px",
        cursor: "pointer",
        fontWeight: "bold"
      }}
    >
      📄 Download PDF Report
    </button>
              {selectedType && (
  <div className="details">
    <h3>Details</h3>

    {data.vulnerabilities[selectedType].map((vuln, index) => (
      <div key={index} className="vuln-box">
        <p><strong>URL:</strong> {vuln.url}</p>
        <p><strong>Input:</strong> {vuln.vulnerable_input}</p>
        <p><strong>Payload:</strong> {vuln.payload || "N/A"}</p>
        <p><strong>Remediation:</strong> {vuln.remediation}</p>
      </div>
    ))}
  </div>
)}
            </>
          )}

        </div>
</div>
      </div>
      </div>
      
  );
}

export default App;