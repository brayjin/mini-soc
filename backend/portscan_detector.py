# portscan_detector.py
import time
import subprocess
import re
from datetime import datetime
import requests

BACKEND_URL = "http://localhost:5000/test-alert"
scan_threshold = 10
scan_window = 5
ip_activity = {}

def add_alert(ip, port_count):
    alert = {
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "ip": ip,
        "type": "Port Scan Detected",
        "ports_scanned": port_count,
        "status": "active"
    }
    print("🚨 Port scan alert:", alert)
    try:
        requests.post(BACKEND_URL, json=alert)
    except Exception as e:
        print("❌ Failed to send alert:", e)

def detect_scan():
    print("🔍 Starting Port Scan Detector...")
    process = subprocess.Popen(
        ['sudo', 'tcpdump', '-l', '-n', 'tcp'],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True
    )

    try:
        for line in process.stdout:
            match = re.search(r'IP (\d+\.\d+\.\d+\.\d+)\.\d+ > .*:(\d+)', line)
            if match:
                ip = match.group(1)
                port = match.group(2)
                now = time.time()

                if ip not in ip_activity:
                    ip_activity[ip] = []

                ip_activity[ip] = [entry for entry in ip_activity[ip] if now - entry[1] <= scan_window]
                ip_activity[ip].append((port, now))

                unique_ports = set(port for port, _ in ip_activity[ip])

                if len(unique_ports) >= scan_threshold:
                    add_alert(ip, len(unique_ports))
                    ip_activity[ip] = []
    except KeyboardInterrupt:
        print("🛑 Stopped Port Scan Detector")

if __name__ == "__main__":
    detect_scan()
