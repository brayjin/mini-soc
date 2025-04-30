# app.py
import sqlite3
from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

DATABASE = 'alerts.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            ip TEXT,
            type TEXT,
            attempts INTEGER,
            ports_scanned INTEGER,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

create_table()

def load_alerts():
    conn = get_db_connection()
    alerts = conn.execute('SELECT * FROM alerts ORDER BY id DESC').fetchall()
    conn.close()
    return [dict(alert) for alert in alerts]

def save_alert(alert):
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO alerts (timestamp, ip, type, attempts, ports_scanned, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        alert.get('timestamp'),
        alert.get('ip'),
        alert.get('type'),
        alert.get('attempts', 0),
        alert.get('ports_scanned', 0),
        alert.get('status', 'active')
    ))
    conn.commit()
    conn.close()

def update_alert_status(ip, status):
    conn = get_db_connection()
    conn.execute('''
        UPDATE alerts SET status = ? WHERE ip = ?
    ''', (status, ip))
    conn.commit()
    conn.close()

@app.route("/alerts", methods=["GET"])
def get_alerts():
    return jsonify(load_alerts())

@app.route("/block/<ip>", methods=["POST"])
def block_ip(ip):
    update_alert_status(ip, 'blocked')
    return jsonify({"status": "success", "message": f"Blocked IP {ip}"})

@app.route("/unblock/<ip>", methods=["POST"])
def unblock_ip(ip):
    update_alert_status(ip, 'active')
    return jsonify({"status": "success", "message": f"Unblocked IP {ip}"})

@app.route("/test-alert", methods=["POST"])
def test_alert():
    alert = request.get_json()
    save_alert(alert)
    socketio.emit('new_alert', alert)
    print("📡 Real-time alert sent:", alert)
    return jsonify({"status": "success", "message": "Alert added and emitted!"})

if __name__ == "__main__":
    print("🚀 Flask backend is running on http://localhost:5000")
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
