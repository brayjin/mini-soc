import subprocess
import re
import time
import json
import requests
from collections import defaultdict

# CONFIG
SCAN_THRESHOLD = 10         # Number of unique ports accessed by same IP within TIME_WINDOW
TIME_WINDOW = 10            # Seconds
FLASK_ALERT_ENDPOINT = "http://localhost:5000/report-portscan"

# State
ip_activity = defaultdict(list)

def extract_connection_info(line):
    match = re.search(r'IP (\d+\.\d+\.\d+\.\d+)\.\d+ > .*:(\d+)', line)
    if match:
        return match.group(1), match.group(2)
    return None, None

def send_alert(ip):
    try:
        response = requests.post(FLASK_ALERT_ENDPOINT, json={'ip': ip})
        print(f"🚨 Port scan alert sent for {ip}: {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to send alert: {e}")

def monitor_packets():
    print("📡 Monitoring for port scans...")
    proc = subprocess.Popen(['tcpdump', '-n', 'tcp'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)

    try:
        for line in proc.stdout:
            src_ip, dst_port = extract_connection_info(line)
            if not src_ip or not dst_port:
                continue

            now = time.time()
            ip_activity[src_ip] = [(p, t) for (p, t) in ip_activity[src_ip] if now - t < TIME_WINDOW]
            ip_activity[src_ip].append((dst_port, now))

            unique_ports = set([p for p, _ in ip_activity[src_ip]])
            if len(unique_ports) >= SCAN_THRESHOLD:
                print(f"🔎 Detected possible port scan from {src_ip} on ports: {list(unique_ports)}")
                send_alert(src_ip)
                ip_activity[src_ip] = []  # Reset
    except KeyboardInterrupt:
        print("🛑 Stopping packet monitor...")
        proc.terminate()

if __name__ == "__main__":
    monitor_packets()
