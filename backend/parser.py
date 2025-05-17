# backend/parser.py
import re
import time
import json
from collections import defaultdict
from datetime import datetime

# Config
LOG_FILE = "/var/log/auth.log"
ALERTS_FILE = "../alerts/alerts.json"
THRESHOLD = 5  # how many failed attempts trigger an alert

# In-memory tracker
failed_logins = defaultdict(int)
already_alerted = set()

def write_alert(ip, count):
    alert = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ip": ip,
        "type": "Brute Force Login Attempt",
        "attempts": count,
        "status": "active"
    }

    print(f"🚨 ALERT: {alert}")

    with open(ALERTS_FILE, "a") as f:
        f.write(json.dumps(alert) + "\n")  # Line-delimited JSON

def monitor_logs():
    print("🔍 Starting SSH log monitoring...")
    with open(LOG_FILE, "r") as log:
        log.seek(0, 2)  # Move to the end of the log file

        while True:
            line = log.readline()
            if not line:
                time.sleep(0.5)
                continue

            match = re.search(r"Failed password.*from (\d+\.\d+\.\d+\.\d+)", line)
            if match:
                ip = match.group(1)
                failed_logins[ip] += 1
                print(f"⚠️  Failed attempt from {ip} (count: {failed_logins[ip]})")

                if failed_logins[ip] >= THRESHOLD and ip not in already_alerted:
                    write_alert(ip, failed_logins[ip])
                    already_alerted.add(ip)

if __name__ == "__main__":
    monitor_logs()
