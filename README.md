# 🛡️ Mini SOC - Real-Time Intrusion Detection & Response Dashboard

A lightweight Security Operations Center (SOC) platform built with Python, Flask, SQLite, React, and Tailwind CSS.

The system monitors suspicious activity on Linux systems, detects SSH brute-force attacks and port scans, stores alerts in SQLite, and allows security analysts to block or unblock malicious IPs directly from the dashboard.

---

## Features

### Detection

* SSH Brute Force Detection
* Port Scan Detection
* Real-Time Alert Generation
* Automatic Alert Persistence

### Response

* Block Malicious IPs
* Unblock Previously Blocked IPs
* Alert Status Tracking
* Firewall Integration (iptables)

### Dashboard

* React + Tailwind UI
* Live Alert Updates
* Alert Statistics
* Alert Management Interface

### Storage

* SQLite Database
* SQLAlchemy ORM
* Persistent Alert History

---

## Architecture

```text
Nmap / Attack Traffic
          │
          ▼
portscan_detector.py
          │
          ▼
      Flask API
          │
          ▼
       SQLite
          ▲
          │
     parser.py
          │
          ▼
     SSH Logs

          │
          ▼
    React Dashboard
```

---

## Project Structure

```text
mini-soc/

├── backend/
│   ├── app.py
│   ├── parser.py
│   ├── portscan_detector.py
│   ├── database.py
│   ├── models.py
│   ├── init_db.py
│   └── soc.db
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   │
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

---

## Backend Setup

### Create Virtual Environment

```bash
cd backend

python -m venv venv

source venv/bin/activate
```

### Install Dependencies

```bash
pip install flask
pip install flask-cors
pip install sqlalchemy
pip install requests
```

### Initialize Database

```bash
python init_db.py
```

Expected:

```text
Database initialized.
```

### Start Flask API

```bash
python app.py
```

Expected:

```text
Running on http://localhost:5000
```

---

## Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

## Detection Services

### SSH Brute Force Detector

```bash
python parser.py
```

Monitors:

```text
journalctl -f
```

or

```text
/var/log/auth.log
```

depending on distribution.

---

### Port Scan Detector

Install tcpdump:

```bash
sudo pacman -S tcpdump
```

Grant permissions:

```bash
sudo setcap cap_net_raw,cap_net_admin=eip $(which tcpdump)
```

Run detector:

```bash
python portscan_detector.py
```

---

## API Endpoints

### Get Alerts

```http
GET /alerts
```

---

### Health Check

```http
GET /health
```

---

### Report Port Scan

```http
POST /report-portscan
```

Body:

```json
{
  "ip": "192.168.1.100"
}
```

---

### Report Brute Force

```http
POST /report-bruteforce
```

Body:

```json
{
  "ip": "192.168.1.100",
  "attempts": 5
}
```

---

### Block IP

```http
POST /block/<ip>
```

---

### Unblock IP

```http
POST /unblock/<ip>
```

---

## Database Schema

### alerts

| Field     | Type    |
| --------- | ------- |
| id        | Integer |
| timestamp | String  |
| ip        | String  |
| type      | String  |
| status    | String  |
| attempts  | Integer |

### blocked_ips

| Field | Type    |
| ----- | ------- |
| id    | Integer |
| ip    | String  |

---

## Testing

### Port Scan Detection

```bash
nmap -sS -p 1-100 192.168.1.10
```

Expected:

* Alert generated
* Stored in SQLite
* Appears on dashboard

### Blocking

Click:

```text
Block
```

Expected:

```bash
sudo iptables -L INPUT -n
```

shows:

```text
DROP all -- <ip> 0.0.0.0/0
```

---

## Future Improvements

* WebSocket Live Updates
* Auto-Blocking Rules
* Alert Severity Levels
* Authentication
* Docker Deployment
* Email Notifications
* SIEM Integration
* Threat Intelligence Feeds

---

## Author

Brayjin J Antony

B.E. Computer Science & Engineering (Cyber Security)

Mini SOC Project for Security Monitoring and Incident Response Demonstration.
