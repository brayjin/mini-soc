from flask import Flask, jsonify, request
from flask_cors import CORS

import ipaddress
import subprocess

from datetime import datetime

from database import SessionLocal
from models import Alert
from models import BlockedIP

app = Flask(__name__)
CORS(app)


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def validate_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def is_ip_blocked(ip):

    result = subprocess.run(
        [
            "iptables",
            "-C",
            "INPUT",
            "-s",
            ip,
            "-j",
            "DROP"
        ],
        capture_output=True,
        text=True
    )

    return result.returncode == 0


def run_iptables_command(args):

    subprocess.run(
        ["sudo", "iptables"] + args,
        check=True,
        capture_output=True,
        text=True
    )


def alert_to_dict(alert):

    return {
        "id": alert.id,
        "timestamp": alert.timestamp,
        "ip": alert.ip,
        "type": alert.type,
        "status": alert.status,
        "attempts": alert.attempts
    }


# --------------------------------------------------
# Routes
# --------------------------------------------------

@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "healthy"
    })


# --------------------------------------------------

@app.route("/alerts", methods=["GET"])
def get_alerts():

    db = SessionLocal()

    try:

        alerts = (
            db.query(Alert)
            .order_by(Alert.id.desc())
            .all()
        )

        return jsonify([
            alert_to_dict(alert)
            for alert in alerts
        ])

    finally:
        db.close()


# --------------------------------------------------

@app.route("/blocked-ips", methods=["GET"])
def get_blocked_ips():

    db = SessionLocal()

    try:

        blocked = db.query(BlockedIP).all()

        return jsonify([
            {
                "id": row.id,
                "ip": row.ip
            }
            for row in blocked
        ])

    finally:
        db.close()


# --------------------------------------------------

@app.route("/block/<ip>", methods=["POST"])
def block_ip(ip):

    if not validate_ip(ip):
        return jsonify({
            "error": "Invalid IP"
        }), 400

    if is_ip_blocked(ip):
        return jsonify({
            "message": "IP already blocked"
        }), 409

    try:

        run_iptables_command([
            "-A",
            "INPUT",
            "-s",
            ip,
            "-j",
            "DROP"
        ])

        db = SessionLocal()

        try:

            existing = (
                db.query(BlockedIP)
                .filter(BlockedIP.ip == ip)
                .first()
            )

            if not existing:

                db.add(
                    BlockedIP(
                        ip=ip
                    )
                )

            alerts = (
                db.query(Alert)
                .filter(Alert.ip == ip)
                .all()
            )

            for alert in alerts:
                alert.status = "blocked"

            db.commit()

        finally:
            db.close()

        return jsonify({
            "message": f"{ip} blocked"
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# --------------------------------------------------

@app.route("/unblock/<ip>", methods=["POST"])
def unblock_ip(ip):

    if not validate_ip(ip):
        return jsonify({
            "error": "Invalid IP"
        }), 400

    if not is_ip_blocked(ip):
        return jsonify({
            "message": "IP is not blocked"
        }), 409

    try:

        run_iptables_command([
            "-D",
            "INPUT",
            "-s",
            ip,
            "-j",
            "DROP"
        ])

        db = SessionLocal()

        try:

            blocked = (
                db.query(BlockedIP)
                .filter(BlockedIP.ip == ip)
                .first()
            )

            if blocked:
                db.delete(blocked)

            alerts = (
                db.query(Alert)
                .filter(Alert.ip == ip)
                .all()
            )

            for alert in alerts:
                alert.status = "active"

            db.commit()

        finally:
            db.close()

        return jsonify({
            "message": f"{ip} unblocked"
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# --------------------------------------------------

@app.route("/report-portscan", methods=["POST"])
def report_portscan():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Missing JSON body"
        }), 400

    ip = data.get("ip")

    if not ip:
        return jsonify({
            "error": "Missing IP"
        }), 400

    if not validate_ip(ip):
        return jsonify({
            "error": "Invalid IP"
        }), 400

    db = SessionLocal()

    try:

        existing = (
            db.query(Alert)
            .filter(
                Alert.ip == ip,
                Alert.type == "Port Scanning Attempt",
                Alert.status == "active"
            )
            .first()
        )

        if not existing:

            db.add(
                Alert(
                    timestamp=current_timestamp(),
                    ip=ip,
                    type="Port Scanning Attempt",
                    status="active",
                    attempts=None
                )
            )

            db.commit()

        return jsonify({
            "message": "Port scan recorded"
        }), 201

    finally:
        db.close()


# --------------------------------------------------

@app.route("/report-bruteforce", methods=["POST"])
def report_bruteforce():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Missing JSON body"
        }), 400

    ip = data.get("ip")
    attempts = data.get("attempts", 0)

    if not ip:
        return jsonify({
            "error": "Missing IP"
        }), 400

    if not validate_ip(ip):
        return jsonify({
            "error": "Invalid IP"
        }), 400

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

        if not existing:

            db.add(
                Alert(
                    timestamp=current_timestamp(),
                    ip=ip,
                    type="Brute Force Login Attempt",
                    status="active",
                    attempts=attempts
                )
            )

            db.commit()

        return jsonify({
            "message": "Bruteforce alert recorded"
        }), 201

    finally:
        db.close()


# --------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )