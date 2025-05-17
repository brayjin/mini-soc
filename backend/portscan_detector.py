import subprocess
import re
import time
import json
import requests
from collections import defaultdict

# CONFIG
SCAN_THRESHOLD = 10         # Unique ports within TIME_WINDOW
TIME_WINDOW = 10            # Seconds to track ports
COOLDOWN = 60               # Seconds to avoid duplicate alerts
FLASK_ALERT_ENDPOINT = "http://localhost:5000/report-portscan"

# STATE
ip_activity = defaultdict(list)
last_alert_time = {}

def extract_connection_info(line):
    # Sample line: IP 192.168.157.1.50514 > 192.168.157.97.22: Flags [S], seq 12345, ...
    match = re.search(r'IP (\d+\.\d+\.\d+\.\d+)\.\d+ > \d+\.\d+\.\d+\.\d+\.(\d+):', line)
    return (match.group(1), match.group(2)) if match else (None, None)

def send_alert(ip, ports):
    now = time.time()
    if ip in last_alert_time and now - last_alert_time[ip] < COOLDOWN:
        return  # Cooldown active, skip alert

    last_alert_time[ip] = now

    try:
        response = requests.post(FLASK_ALERT_ENDPOINT, json={
            'ip': ip,
            'ports': list(ports),
            'timestamp': now
        })
        print(f"🚨 Port scan alert sent for {ip}: {response.status_code}")
    except requests.RequestException as e:
        print(f"❌ Failed to send alert: {e}")

def monitor_packets():
    print("📡 Monitoring for port scans...")
    proc = subprocess.Popen(
        ['sudo', 'tcpdump', '-n', '-l', '-i', 'any', 'tcp[tcpflags] & tcp-syn != 0'],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True
    )

    try:
        for line in proc.stdout:
            src_ip, dst_port = extract_connection_info(line)
            if not src_ip or not dst_port:
                continue

            now = time.time()
            ip_activity[src_ip] = [(p, t) for (p, t) in ip_activity[src_ip] if now - t < TIME_WINDOW]
            ip_activity[src_ip].append((dst_port, now))

            unique_ports = {p for p, _ in ip_activity[src_ip]}
            if len(unique_ports) >= SCAN_THRESHOLD:
                print(f"🔎 Detected possible port scan from {src_ip} on ports: {list(unique_ports)}")
                send_alert(src_ip, unique_ports)
                ip_activity[src_ip].clear()
    except KeyboardInterrupt:
        print("🛑 Stopping packet monitor...")
        proc.terminate()

if __name__ == "__main__":
    monitor_packets()
