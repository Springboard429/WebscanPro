import os
import sys
import json
import time
import subprocess
import threading
import queue
import re
from queue import Queue, Empty
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Global variables for process management
process_queue = Queue()
stop_event = threading.Event()

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>WebScanPro</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="text"] {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin-right: 10px;
        }
        button:hover {
            background-color: #45a049;
        }
        #cancelBtn {
            background-color: #f44336;
        }
        #cancelBtn:hover {
            background-color: #d32f2f;
        }
        .vuln {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
        }
        .status {
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
        }
        .info {
            background-color: #e7f3fe;
            border-left: 4px solid #2196F3;
        }
        .error {
            background-color: #ffebee;
            border-left: 4px solid #f44336;
        }
        .success {
            background-color: #e8f5e9;
            border-left: 4px solid #4CAF50;
        }
        .progress-container {
            width: 100%;
            background-color: #f1f1f1;
            border-radius: 4px;
            margin: 10px 0;
            display: none;
        }
        .progress-bar {
            width: 0%;
            height: 20px;
            background-color: #28a745;
            border-radius: 4px;
            text-align: center;
            line-height: 20px;
            color: white;
            transition: width 0.3s;
        }
        .spinner {
            border: 4px solid rgba(0, 0, 0, 0.1);
            width: 20px;
            height: 20px;
            border-radius: 50%;
            border-left-color: #09f;
            animation: spin 1s linear infinite;
            margin-right: 10px;
            display: inline-block;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <h1>WebScanPro - Vulnerability Scanner</h1>
    <div class="container">
        <form id="scanForm" onsubmit="startScan(); return false;">
            <div class="form-group">
                <label for="url">Target URL:</label>
                <input type="text" id="url" value="http://testphp.vulnweb.com/artists.php?artist=1" required>
            </div>
            <div class="form-group">
                <label>Scan Type:</label><br>
                <input type="radio" id="scanAll" name="scanType" value="all" checked>
                <label for="scanAll">All</label>
                <input type="radio" id="scanXSS" name="scanType" value="xss">
                <label for="scanXSS">XSS Only</label>
                <input type="radio" id="scanSQL" name="scanType" value="sqli">
                <label for="scanSQL">SQLi Only</label>
            </div>
            <button type="submit" id="scanButton">Start Scan</button>
            <button type="button" id="cancelBtn" style="display: none;">Cancel Scan</button>
        </form>
        <div class="progress-container" id="progressContainer">
            <div class="progress-bar" id="progressBar">0%</div>
        </div>
        <div id="status" class="status" style="display: none;"></div>
        <div id="results"></div>
    </div>

    <script>
        let scanInProgress = false;
        let currentRequest = null;

        function updateStatus(message, type = 'info') {
            const statusDiv = document.getElementById('status');
            statusDiv.innerHTML = type === 'scanning' 
                ? `<span class="spinner"></span>${message}` 
                : message;
            statusDiv.className = 'status ' + type;
            statusDiv.style.display = 'block';
            return statusDiv;
        }

        function updateProgress(percent) {
            const progressBar = document.getElementById('progressBar');
            const progressContainer = document.getElementById('progressContainer');
            progressBar.style.width = percent + '%';
            progressBar.textContent = percent + '%';
            progressContainer.style.display = 'block';
        }

        function addResult(html) {
            const resultsDiv = document.getElementById('results');
            const div = document.createElement('div');
            div.className = 'vuln';
            div.innerHTML = html;
            resultsDiv.appendChild(div);
        }

        function resetUI() {
            document.getElementById('scanButton').disabled = false;
            document.getElementById('scanButton').textContent = 'Start New Scan';
            document.getElementById('cancelBtn').style.display = 'none';
            document.getElementById('progressContainer').style.display = 'none';
            if (currentRequest) {
                currentRequest.abort();
                currentRequest = null;
            }
            scanInProgress = false;
        }

        function startScan() {
            if (scanInProgress) return;
            
            const url = document.getElementById('url').value;
            const scanType = document.querySelector('input[name="scanType"]:checked').value;
            const scanButton = document.getElementById('scanButton');
            const cancelBtn = document.getElementById('cancelBtn');
            const resultsDiv = document.getElementById('results');
            
            // Reset UI
            resultsDiv.innerHTML = '';
            updateStatus('Initializing scan...', 'scanning');
            scanButton.disabled = true;
            scanButton.textContent = 'Scanning...';
            cancelBtn.style.display = 'inline-block';
            document.getElementById('progressContainer').style.display = 'block';
            updateProgress(0);
            
            scanInProgress = true;
            let progress = 0;
            const progressInterval = setInterval(() => {
                if (!scanInProgress) {
                    clearInterval(progressInterval);
                    return;
                }
                progress = Math.min(progress + Math.random() * 5, 90);
                updateProgress(Math.floor(progress));
            }, 500);
            
            // Create a new AbortController for the fetch request
            const controller = new AbortController();
            currentRequest = controller;
            
            fetch('/scan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    url: url, 
                    scan_type: scanType 
                }),
                signal: controller.signal
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                clearInterval(progressInterval);
                updateProgress(100);
                
                if (data.status === 'completed') {
                    updateStatus(`Scan completed! Found ${data.vulnerabilities.length} vulnerabilities.`, 'success');
                    if (data.vulnerabilities.length > 0) {
                        data.vulnerabilities.forEach(vuln => {
                            addResult(vuln);
                        });
                    } else {
                        addResult('No vulnerabilities found!');
                    }
                } else {
                    updateStatus('Error: ' + (data.message || 'Unknown error occurred'), 'error');
                    if (data.output) {
                        addResult(`<pre>${data.output}</pre>`);
                    }
                }
            })
            .catch(error => {
                clearInterval(progressInterval);
                if (error.name === 'AbortError') {
                    updateStatus('Scan was cancelled', 'error');
                } else {
                    updateStatus('Error: ' + (error.message || 'An error occurred'), 'error');
                    console.error('Error:', error);
                }
            })
            .finally(() => {
                resetUI();
            });
            
            // Add cancel button handler
            cancelBtn.onclick = function() {
                clearInterval(progressInterval);
                controller.abort();
                updateStatus('Cancelling scan...', 'error');
                resetUI();
                fetch('/cancel_scan', {
                    method: 'POST'
                });
            };
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Render the main page"""
    with open('templates/index.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/test_scan', methods=['GET'])
def test_scan():
    """Test endpoint to verify scanner functionality"""
    test_url = "http://testphp.vulnweb.com/artists.php?artist=1"
    print(f"\n=== STARTING TEST SCAN ===")
    print(f"Target URL: {test_url}")
    
    try:
        # Make a simple HTTP request to verify connectivity
        import requests
        response = requests.get(test_url, timeout=10)
        print(f"HTTP Status: {response.status_code}")
        print("Headers:", response.headers)
        print("Response length:", len(response.text))
        
        return jsonify({
            'status': 'success',
            'url': test_url,
            'status_code': response.status_code,
            'content_length': len(response.text)
        })
    except Exception as e:
        print(f"Test scan failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/scan', methods=['POST'])
def scan():
    data = request.json
    url = data.get('url', '')
    scan_type = data.get('scan_type', 'all')
    username = data.get('username', '')
    password = data.get('password', '')

    print(f"\n=== STARTING SCAN ===")
    print(f"URL: {url}")
    print(f"Scan Type: {scan_type}")
    print(f"Username: {username}")
    print(f"Password: {'*' * len(password) if password else 'None'}")

    try:
        # Test connectivity first
        try:
            import requests
            print("\n[DEBUG] Testing connection to target URL...")
            response = requests.get(url, timeout=10)
            print(f"[DEBUG] Connection successful. Status: {response.status_code}")
        except Exception as e:
            print(f"[DEBUG] Connection test failed: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'Cannot connect to target URL: {str(e)}'
            })

        # Clear any previous stop events
        stop_event.clear()

        # Create queues for thread-safe communication
        output_queue = queue.Queue()
        error_queue = queue.Queue()
        output_lines = []
        
        def enqueue_output(pipe, queue):
            for line in iter(pipe.readline, ''):
                # Strip ANSI color codes from output
                clean_line = re.sub(r'\x1b\[[0-9;]*[0-9;]*m', '', line)
                queue.put(clean_line)
                output_lines.append(clean_line.strip())
            pipe.close()

        # Create the command with debug output
        cmd = [
            'python', 'main.py',
            '--url', url,
            '--crawl-depth', '1',  # Limited crawl depth for speed
            '--threads', '1',      # Use only 1 thread
            '--no-external-apis',  # Don't use external APIs
            '--format', 'json',    # Output as JSON
            '--verbose'            # Enable verbose output
        ]
        
        # Add scan type if specified
        if scan_type in ['xss', 'sqli']:
            cmd.extend(['--scan-type', scan_type])
        elif scan_type == 'quick':
            # Quick scan mode - only SQLi with limited scope
            cmd.extend(['--scan-type', 'sqli'])
            cmd.extend(['--crawl-depth', '0'])  # Only scan the main URL
        
        # Add authentication if provided
        if username:
            cmd.extend(['--username', username])
        if password:
            cmd.extend(['--password', password])
            
        print(f"[DEBUG] Command: {' '.join(cmd)}")
        print(f"[DEBUG] Working directory: {os.getcwd()}")
        print(f"[DEBUG] Python executable: {sys.executable}")
        
        # Start the process with pipes for output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Redirect stderr to stdout for logging
            text=True,
            bufsize=1,  # Line buffered
            universal_newlines=True,
            cwd=os.getcwd()  # Ensure we run in the correct directory
        )
        
        # Start thread to read stdout (stderr is redirected to stdout)
        stdout_thread = threading.Thread(
            target=enqueue_output,
            args=(process.stdout, output_queue)
        )
        
        # Make thread daemon so it'll exit when the main program exits
        stdout_thread.daemon = True
        
        # Start the thread
        stdout_thread.start()
        
        # Store process in queue for potential cancellation
        process_queue.put(process)
        
        # Set timeout for the scan (in seconds)
        timeout = 120  # Reduced timeout as scanner is now faster
        print(f"\n[DEBUG] Starting scan with timeout: {timeout} seconds")
        
        # Record start time for timeout calculation
        start_time = time.time()
        
        # Read output in real-time with timeout
        while True:
            # Check for process completion
            return_code = process.poll()
            
            # Read available output from queue
            while True:
                try:
                    line = output_queue.get_nowait()
                    line = line.strip()
                    print(f"[SCAN] {line}")
                except queue.Empty:
                    break
            
            # Check for completion
            if return_code is not None:
                # Get any remaining output safely
                try:
                    remaining_output = process.stdout.read()
                    if remaining_output:
                        print(f"[SCAN] {remaining_output.strip()}")
                        output_lines.append(remaining_output.strip())
                except (ValueError, OSError) as e:
                    print(f"[DEBUG] Could not read remaining output: {e}")
                
                result = subprocess.CompletedProcess(
                    process.args, 
                    return_code, 
                    '\n'.join(output_lines),
                    ''
                )
                print(f"\n[DEBUG] Process completed with return code: {return_code}")
                break
            
            # Check for timeout
            if time.time() - start_time > timeout:
                print(f"\n[DEBUG] === TIMEOUT AFTER {timeout} SECONDS ===")
                print("[DEBUG] Last few lines of output:")
                for line in output_lines[-10:]:
                    print(f"> {line}")
                
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                
                return jsonify({
                    'status': 'error',
                    'message': f'Scan timed out after {timeout} seconds',
                    'output': '\n'.join(output_lines[-20:])
                })
            
            # Check for stop event
            if stop_event.is_set():
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                return jsonify({
                    'status': 'cancelled',
                    'message': 'Scan was cancelled by user',
                    'output': '\n'.join(output_lines[-20:]) if output_lines else 'No output captured'
                })
            
            time.sleep(0.1)
        
        # Process completed, check results
        if result.returncode == 0:
            try:
                # Instead of parsing from stdout, read the JSON report file directly
                import glob
                
                # Find the most recent JSON report file
                reports_dir = 'reports'
                json_files = glob.glob(os.path.join(reports_dir, 'webscanpro_report_*.json'))
                
                print(f"[DEBUG] Looking for JSON files in {reports_dir}")
                print(f"[DEBUG] Found JSON files: {json_files}")
                
                if json_files:
                    # Get the most recent file
                    latest_file = max(json_files, key=os.path.getctime)
                    print(f"[DEBUG] Reading JSON from file: {latest_file}")
                    
                    with open(latest_file, 'r', encoding='utf-8') as f:
                        report_data = json.load(f)
                    
                    print(f"\n[DEBUG] Scan completed successfully")
                    print(f"[DEBUG] Found {len(report_data.get('vulnerabilities', []))} vulnerabilities")
                    print(f"[DEBUG] Vulnerabilities: {report_data.get('vulnerabilities', [])}")
                    
                    vulnerabilities = []
                    for vuln in report_data.get('vulnerabilities', []):
                        vuln_obj = {
                            'type': vuln.get('type', 'Vulnerability'),
                            'url': vuln.get('url', 'N/A'),
                            'description': vuln.get('description', 'No description'),
                            'severity': vuln.get('severity', 'Medium'),
                            'payload': vuln.get('payload', 'N/A')
                        }
                        vulnerabilities.append(vuln_obj)
                    
                    print(f"[DEBUG] Returning {len(vulnerabilities)} vulnerabilities to frontend")
                    
                    return jsonify({
                        'status': 'completed',
                        'url': url,
                        'vulnerabilities': vulnerabilities
                    })
                else:
                    raise Exception("No JSON report file found")
                    
            except Exception as e:
                error_msg = f'Failed to read scan results: {str(e)}'
                print(f"\n[ERROR] {error_msg}")
                print(f"[DEBUG] Exception details: {str(e)}")
                    
                return jsonify({
                    'status': 'error',
                    'message': f'Failed to read scan results: {str(e)}',
                    'output': result.stdout
                })
        else:
            error_msg = f'Scan failed with return code {result.returncode}'
            print(f"\n[ERROR] {error_msg}")
            print(f"[DEBUG] stdout: {result.stdout}")
            print(f"[DEBUG] stderr: {result.stderr}")
            print(f"[DEBUG] Last 10 lines of output:")
            for line in output_lines[-10:]:
                print(f"> {line}")
            return jsonify({
                'status': 'error',
                'message': f'{error_msg}: {result.stderr}',
                'output': result.stdout,
                'debug_output': '\n'.join(output_lines[-20:])
            })
            
    except Exception as e:
        error_msg = f'Error during scan: {str(e)}'
        print(f"\n[ERROR] {error_msg}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': error_msg
        })

@app.route('/cancel_scan', methods=['POST'])
def cancel_scan():
    """Endpoint to cancel the current scan"""
    stop_event.set()
    return jsonify({'status': 'cancelling'})

@app.route('/scan_history', methods=['GET'])
def get_scan_history():
    """Get recent scan results"""
    try:
        import glob
        reports_dir = 'reports'
        json_files = glob.glob(os.path.join(reports_dir, 'webscanpro_report_*.json'))
        
        history = []
        for file_path in sorted(json_files, key=os.path.getctime, reverse=True)[:10]:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                history.append({
                    'timestamp': data.get('report_generated', ''),
                    'target_url': data.get('target_url', ''),
                    'vulnerabilities_count': len(data.get('vulnerabilities', [])),
                    'scan_time': data.get('elapsed_time', 0)
                })
        
        return jsonify({'history': history})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/favicon.ico')
def favicon():
    return '', 204  # Return No Content

def cleanup_processes():
    """Clean up any running processes on shutdown"""
    while not process_queue.empty():
        try:
            process = process_queue.get_nowait()
            if process.poll() is None:  # Process is still running
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        except Empty:
            break

if __name__ == '__main__':
    # Create reports directory if it doesn't exist
    os.makedirs('reports', exist_ok=True)
    
    # Register cleanup on exit
    import atexit
    atexit.register(cleanup_processes)
    
    # Run the app with multithreading enabled
    app.run(debug=True, port=5000, threaded=True)
