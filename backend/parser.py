import re
import time
import json
import os
from collections import defaultdict
from datetime import datetime

# Config
LOG_FILE = "/var/log/auth.log"
ALERTS_FILE = "../alerts/alerts.json"
THRESHOLD = 2
COOLDOWN = 60  # Seconds

# Trackers
failed_logins = defaultdict(int)
last_alert_time = {}

def write_alert(ip, count):
    alert = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ip": ip,
        "type": "Brute Force Login Attempt",
        "attempts": count,
        "status": "active"
    }

    print(f"🚨 ALERT: {alert}")

    try:
        # Load existing alerts
        alerts = []
        if os.path.exists(ALERTS_FILE) and os.path.getsize(ALERTS_FILE) > 0:
            with open(ALERTS_FILE, "r") as f:
                alerts = json.load(f)

        alerts.append(alert)

        # Write updated alerts back to file
        with open(ALERTS_FILE, "w") as f:
            json.dump(alerts, f, indent=2)

    except Exception as e:
        print(f"❌ Error writing alert: {e}")

def monitor_logs():
    print("🔍 Starting SSH log monitoring...")
    with open(LOG_FILE, "r") as log:
        log.seek(0, 2)  # Jump to end of file

        while True:
            line = log.readline()
            if not line:
                time.sleep(0.5)
                continue

            match = re.search(r"Failed password.*from (\d+\.\d+\.\d+\.\d+)", line)
            if match:
                ip = match.group(1)
                failed_logins[ip] += 1
                print(f"⚠️ Failed attempt from {ip} (count: {failed_logins[ip]})")

                now = time.time()
                if failed_logins[ip] >= THRESHOLD:
                    if ip not in last_alert_time or now - last_alert_time[ip] >= COOLDOWN:
                        write_alert(ip, failed_logins[ip])
                        last_alert_time[ip] = now

if __name__ == "__main__":
    monitor_logs()
