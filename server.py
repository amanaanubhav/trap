import subprocess
import sys
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = int(os.environ.get("PORT", 8501))

def run_streamlit():
    """try launching the main streamlit app"""
    try:
        proc = subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            f"--server.port={PORT}",
            "--server.address=0.0.0.0",
            "--server.enableCORS=false",
            "--server.enableXsrfProtection=false",
        ])
        return proc.returncode == 0
    except Exception as e:
        print(f"streamlit failed to start: {e}")
        return False

def run_fallback():
    """serve index.html as a static fallback"""
    print(f"serving fallback page on port {PORT}")
    server = HTTPServer(("0.0.0.0", PORT), SimpleHTTPRequestHandler)
    server.serve_forever()

if __name__ == "__main__":
    print(f"starting trap on port {PORT}")
    success = run_streamlit()
    if not success:
        run_fallback()
