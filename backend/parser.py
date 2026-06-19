import re
import time
import os
import subprocess

from collections import defaultdict
from datetime import datetime

from database import SessionLocal
from models import Alert

# --------------------------------------------------
# Configuration
# --------------------------------------------------

THRESHOLD = 3
COOLDOWN = 60

# --------------------------------------------------
# State
# --------------------------------------------------

failed_logins = defaultdict(int)
last_alert_time = {}

# --------------------------------------------------
# Database
# --------------------------------------------------

def alert_exists(ip):

    db = SessionLocal()

    try:

        existing = (
            db.query(Alert)
            .filter(
                Alert.ip == ip,
                Alert.type == "Brute Force Login Attempt",
                Alert.status == "active"
            )
            .first()
        )

        return existing is not None

    finally:
        db.close()


def write_alert(ip, count):

    if alert_exists(ip):
        return

    db = SessionLocal()

    try:

        alert = Alert(
            timestamp=datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            ip=ip,
            type="Brute Force Login Attempt",
            status="active",
            attempts=count
        )

        db.add(alert)
        db.commit()

        print(
            f"🚨 ALERT CREATED | "
            f"IP={ip} "
            f"ATTEMPTS={count}"
        )

    except Exception as e:

        db.rollback()

        print(
            f"❌ Failed to insert alert: {e}"
        )

    finally:
        db.close()


# --------------------------------------------------
# Login Processing
# --------------------------------------------------

def process_failed_login(ip):

    failed_logins[ip] += 1

    print(
        f"⚠️ Failed login from {ip} "
        f"(count={failed_logins[ip]})"
    )

    now = time.time()

    if failed_logins[ip] < THRESHOLD:
        return

    if (
        ip not in last_alert_time
        or now - last_alert_time[ip] >= COOLDOWN
    ):

        write_alert(
            ip,
            failed_logins[ip]
        )

        last_alert_time[ip] = now


# --------------------------------------------------
# Arch Linux
# --------------------------------------------------

def monitor_journal():

    print(
        "🔍 Monitoring SSH failures "
        "using journalctl..."
    )

    proc = subprocess.Popen(
        [
            "journalctl",
            "-f",
            "-n",
            "0"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True
    )

    try:

        for line in proc.stdout:

            match = re.search(
                r"Failed password.*from (\d+\.\d+\.\d+\.\d+)",
                line
            )

            if not match:
                continue

            ip = match.group(1)

            if ip.startswith("127."):
                continue

            process_failed_login(ip)

    except KeyboardInterrupt:

        print(
            "\n🛑 Stopping journal monitor..."
        )

        proc.terminate()

        try:
            proc.wait(timeout=2)
        except Exception:
            proc.kill()


# --------------------------------------------------
# Ubuntu / Debian
# --------------------------------------------------

def monitor_auth_log():

    log_file = "/var/log/auth.log"

    print(
        f"🔍 Monitoring {log_file}..."
    )

    with open(log_file, "r") as log:

        log.seek(0, os.SEEK_END)

        while True:

            line = log.readline()

            if not line:
                time.sleep(0.5)
                continue

            match = re.search(
                r"Failed password.*from (\d+\.\d+\.\d+\.\d+)",
                line
            )

            if not match:
                continue

            ip = match.group(1)

            if ip.startswith("127."):
                continue

            process_failed_login(ip)


# --------------------------------------------------
# Auto Detection
# --------------------------------------------------

def monitor_logs():

    if os.path.exists(
        "/var/log/auth.log"
    ):
        monitor_auth_log()
    else:
        monitor_journal()


# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":

    print(
        "🚀 Mini-SOC Brute Force Detector"
    )

    print(
        f"🎯 Threshold: {THRESHOLD}"
    )

    print(
        f"⏳ Cooldown: {COOLDOWN}s"
    )

    monitor_logs()