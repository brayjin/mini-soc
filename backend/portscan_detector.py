import subprocess
import re
import time
import requests

from collections import defaultdict

# --------------------------------------------------
# Configuration
# --------------------------------------------------

SCAN_THRESHOLD = 20
TIME_WINDOW = 10
COOLDOWN = 60

FLASK_ALERT_ENDPOINT = "http://localhost:5000/report-portscan"

# --------------------------------------------------
# State
# --------------------------------------------------

ip_activity = defaultdict(list)
last_alert_time = {}

# --------------------------------------------------
# Helpers
# --------------------------------------------------

def extract_connection_info(line):
    """
    Example:

    IP 192.168.1.100.50412 > 192.168.1.5.22:
    """

    match = re.search(
        r"IP (\d+\.\d+\.\d+\.\d+)\.\d+ > \d+\.\d+\.\d+\.\d+\.(\d+):",
        line
    )

    if not match:
        return None, None

    return match.group(1), match.group(2)


def cleanup_old_entries(ip, now):

    ip_activity[ip] = [
        (port, timestamp)
        for port, timestamp in ip_activity[ip]
        if now - timestamp < TIME_WINDOW
    ]


def send_alert(ip, ports):

    now = time.time()

    if (
        ip in last_alert_time
        and now - last_alert_time[ip] < COOLDOWN
    ):
        return

    last_alert_time[ip] = now

    payload = {
        "ip": ip,
        "ports": sorted(list(ports)),
        "timestamp": now
    }

    try:

        response = requests.post(
            FLASK_ALERT_ENDPOINT,
            json=payload,
            timeout=5
        )

        print(
            f"🚨 Alert sent | "
            f"IP={ip} | "
            f"Ports={len(ports)} | "
            f"Status={response.status_code}"
        )

    except requests.RequestException as e:

        print(
            f"❌ Failed to send alert: {e}"
        )


# --------------------------------------------------
# Packet Monitoring
# --------------------------------------------------

def monitor_packets():

    print("🚀 Mini-SOC Port Scan Detector")
    print(f"🎯 Threshold: {SCAN_THRESHOLD}")
    print(f"⏳ Window: {TIME_WINDOW}s")
    print(f"🔄 Cooldown: {COOLDOWN}s")

    try:

        proc = subprocess.Popen(
            [
                "tcpdump",
                "-n",
                "-l",
                "-i",
                "any",
                "tcp[tcpflags] & tcp-syn != 0"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )

    except FileNotFoundError:

        print(
            "❌ tcpdump not installed.\n"
            "Install with:\n"
            "sudo pacman -S tcpdump"
        )

        return

    try:

        for line in proc.stdout:

            src_ip, dst_port = extract_connection_info(line)

            if not src_ip:
                continue

            if not dst_port:
                continue

            # Ignore localhost
            if src_ip.startswith("127."):
                continue

            now = time.time()

            cleanup_old_entries(
                src_ip,
                now
            )

            ip_activity[src_ip].append(
                (
                    dst_port,
                    now
                )
            )

            unique_ports = {
                port
                for port, _
                in ip_activity[src_ip]
            }

            if len(unique_ports) >= SCAN_THRESHOLD:

                print("\n🔎 PORT SCAN DETECTED")
                print(f"📍 Source: {src_ip}")
                print(
                    f"🎯 Unique Ports: "
                    f"{len(unique_ports)}"
                )

                print(
                    f"🔢 Ports: "
                    f"{sorted(unique_ports)}"
                )

                send_alert(
                    src_ip,
                    unique_ports
                )

                ip_activity[src_ip].clear()

    except KeyboardInterrupt:

        print("\n🛑 Stopping detector...")

        proc.terminate()

        try:
            proc.wait(timeout=2)
        except Exception:
            proc.kill()


# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":
    monitor_packets()