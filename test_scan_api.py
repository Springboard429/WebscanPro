import requests
import json

# Test the scan API directly
url = "http://localhost:5000/scan"
data = {
    "url": "http://localhost:45/",
    "scan_type": "sqli", 
    "username": "admin",
    "password": "password"
}

print("Sending request to:", url)
print("Data:", json.dumps(data, indent=2))

try:
    response = requests.post(url, json=data, timeout=60)
    print("\nResponse Status:", response.status_code)
    print("Response Headers:", dict(response.headers))
    print("Response Text:", response.text)
    
    if response.headers.get('content-type', '').startswith('application/json'):
        result = response.json()
        print("\nParsed Result:")
        print("  Status:", result.get('status'))
        print("  Message:", result.get('message'))
        print("  Vulnerabilities:", len(result.get('vulnerabilities', [])))
        
        if result.get('vulnerabilities'):
            for i, vuln in enumerate(result['vulnerabilities'][:3]):
                print(f"    {i+1}. {vuln.get('type', 'Unknown')} - {vuln.get('url', 'N/A')}")
    else:
        print("Response is not JSON")
        
except Exception as e:
    print(f"Request failed: {e}")
    import traceback
    traceback.print_exc()
