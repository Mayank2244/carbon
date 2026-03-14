
import subprocess
import re
import time
import os
import signal
import sys
import atexit

# Paths
FRONTEND_API_FILE = "frontend/src/services/api.js"
BACKEND_PORT = 8000
FRONTEND_PORT = 5173

original_api_content = None

def restore_api_file():
    if original_api_content:
        print("\nRestoring api.js...")
        with open(FRONTEND_API_FILE, 'w') as f:
            f.write(original_api_content)

def start_tunnel(port, name):
    print(f"Starting {name} tunnel on port {port}...")
    # --url creates a quick tunnel (no auth required)
    proc = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", f"http://127.0.0.1:{port}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True
    )
    
    url = None
    # Read stderr for the URL
    while True:
        line = proc.stderr.readline()
        if not line:
            break
        # print(f"[{name}] {line.strip()}") 
        match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
        if match:
            url = match.group(0)
            break
    
    if not url:
        print(f"Failed to find URL for {name}. Stderr dump:")
        print(proc.stderr.read())
        raise Exception(f"Failed to get {name} tunnel URL")
    
    print(f"{name} Tunnel URL: {url}")
    return proc, url

def update_frontend_api(new_url):
    global original_api_content
    print(f"Updating {FRONTEND_API_FILE} with {new_url}...")
    with open(FRONTEND_API_FILE, 'r') as f:
        original_api_content = f.read()
    
    # Regex replace to be safe
    new_content = re.sub(
        r"http://127\.0\.0\.1:8000", 
        new_url, 
        original_api_content
    )
    
    with open(FRONTEND_API_FILE, 'w') as f:
        f.write(new_content)

def main():
    # Register cleanup
    atexit.register(restore_api_file)

    # 1. Start Backend Tunnel
    try:
        backend_proc, backend_url = start_tunnel(BACKEND_PORT, "Backend")
    except Exception as e:
        print(f"Error starting backend tunnel: {e}")
        return

    # 2. Update Frontend Code
    try:
        update_frontend_api(backend_url)
    except Exception as e:
        print(f"Error updating frontend: {e}")
        backend_proc.terminate()
        return

    # 3. Start Frontend Tunnel
    # Wait a moment for Vite HMR (if running) or simply for the file write to settle
    time.sleep(2)
    
    try:
        frontend_proc, frontend_url = start_tunnel(FRONTEND_PORT, "Frontend")
    except Exception as e:
        print(f"Error starting frontend tunnel: {e}")
        backend_proc.terminate()
        return
    
    print("\n" + "="*60)
    print(f"🚀 LIVE DEPLOYMENT READY")
    print(f"🌍 Public App URL:    {frontend_url}")
    print(f"🔗 Backend API URL:   {backend_url}")
    print("="*60 + "\n")
    print("Press Ctrl+C to stop tunnels and restore local config.")
    
    try:
        # Keep alive
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\nStopping tunnels...")
        backend_proc.terminate()
        frontend_proc.terminate()

if __name__ == "__main__":
    main()
