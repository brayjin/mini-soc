from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import subprocess
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

ALERTS_FILE = '../alerts/alerts.json'
print("Alerts file path:", os.path.abspath(ALERTS_FILE))


def current_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def load_alerts():
    if not os.path.exists(ALERTS_FILE):
        print("Alerts file not found, returning empty list.")
        return []
    with open(ALERTS_FILE, 'r') as f:
        try:
            alerts = json.load(f)
            print(f"Loaded alerts: {alerts}")
            return alerts
        except json.JSONDecodeError:
            print("❌ Invalid JSON format, resetting alerts to empty list...")
            return []


def save_alerts(alerts):
    print("Saving alerts to file...")
    try:
        with open(ALERTS_FILE, 'w') as f:
            json.dump(alerts, f, indent=2)
        print("✅ Alerts saved successfully.")
    except Exception as e:
        print(f"❌ Error saving alerts: {e}")


def is_ip_blocked(ip):
    result = subprocess.run(['sudo', 'iptables', '-C', 'INPUT', '-s', ip, '-j', 'DROP'],
                            capture_output=True)
    return result.returncode == 0


def run_iptables_command(args):
    try:
        subprocess.run(['sudo', 'iptables'] + args, check=True)
        print("✅ Executed:", ' '.join(['iptables'] + args))
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to execute iptables command: {e}")
        raise


@app.route('/alerts', methods=['GET'])
def get_alerts():
    alerts = load_alerts()
    return jsonify(alerts)


@app.route('/block/<ip>', methods=['POST'])
def block_ip(ip):
    alerts = load_alerts()
    print(f"Attempting to block IP: {ip}")

    if is_ip_blocked(ip):
        return jsonify({"message": f"IP {ip} is already blocked"}), 409

    found = False
    for alert in alerts:
        if alert['ip'] == ip:
            alert['status'] = 'blocked'
            found = True
    if not found:
        alerts.append({
            "timestamp": current_timestamp(),
            "ip": ip,
            "type": "Manual Block",
            "status": "blocked"
        })
    save_alerts(alerts)

    try:
        run_iptables_command(['-A', 'INPUT', '-s', ip, '-j', 'DROP'])
        return jsonify({"message": f"IP {ip} blocked"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/unblock/<ip>', methods=['POST'])
def unblock_ip(ip):
    alerts = load_alerts()
    print(f"Attempting to unblock IP: {ip}")

    if not is_ip_blocked(ip):
        return jsonify({"message": f"IP {ip} is not currently blocked"}), 409

    try:
        run_iptables_command(['-D', 'INPUT', '-s', ip, '-j', 'DROP'])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    found = False
    for alert in alerts:
        if alert['ip'] == ip:
            alert['status'] = 'active'
            found = True
    if not found:
        alerts.append({
            "timestamp": current_timestamp(),
            "ip": ip,
            "type": "Manual Unblock",
            "status": "active"
        })
    save_alerts(alerts)

    return jsonify({"message": f"IP {ip} unblocked"}), 200


# 🔍 NEW: Report a Port Scanning Attempt
@app.route('/report-portscan', methods=['POST'])
def report_port_scan():
    data = request.get_json()
    ip = data.get('ip')

    if not ip:
        return jsonify({"error": "Missing 'ip' in request"}), 400

    alerts = load_alerts()

    alerts.append({
        "timestamp": current_timestamp(),
        "ip": ip,
        "type": "Port Scanning Attempt",
        "status": "active"
    })

    save_alerts(alerts)
    return jsonify({"message": f"Port scan attempt by {ip} recorded"}), 201


if __name__ == '__main__':
    app.run(debug=True)

