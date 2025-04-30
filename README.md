---

## 🛡️ Mini SOC: Real-Time Intrusion Detection Dashboard

A lightweight Security Operations Center (SOC) system that detects suspicious activities like SSH brute-force attacks and port scanning on a Linux server, and provides a live dashboard with block/unblock controls.

---

### 📁 Project Structure

```
mini-soc-project/
├── backend/
│   ├── app.py                 # Flask backend with WebSocket support
│   ├── alerts/                # JSON-based alert log storage
│   ├── ssh_detector.py        # SSH brute-force detection logic
│   └── portscan_detector.py   # Port scanning detection logic
├── frontend/
│   ├── src/
│   │   └── App.jsx            # React frontend
│   └── index.html, etc.       # Vite setup
└── README.md                  # You're here!
```

---

### ⚙️ Features

- ✅ SSH Brute-force detection using `/var/log/auth.log`
- ✅ Port Scan detection using `tcpdump`
- ✅ Flask REST API + WebSocket backend
- ✅ React + Tailwind CSS dashboard
- ✅ Real-time alerting
- ✅ IP block/unblock using `iptables`
- ✅ Persistent alert logs (JSON)
- 🔒 Simple status view (`active` / `blocked`)

---

## 🚀 Getting Started

### 🐍 Backend (Flask API)

#### 1. Install dependencies

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install flask flask-socketio eventlet
```

#### 2. Run the backend

```bash
python3 app.py
```

You should see:

```
🚀 Backend running on http://localhost:5000
```

---

### ⚛️ Frontend (React UI)

#### 1. Setup

```bash
cd frontend
npm install
```

#### 2. Run frontend

```bash
npm run dev
```

Visit `http://localhost:5173`

---

## 🔍 Detectors

### ✅ SSH Brute-force Detector

```bash
cd backend
sudo python3 ssh_detector.py
```

This parses `/var/log/auth.log` and sends alerts to `/test-alert`.

---

### ✅ Port Scan Detector

```bash
cd backend
sudo python3 portscan_detector.py
```

Scans incoming TCP traffic and detects rapid port scanning.

> ⚠️ Requires `tcpdump`:
```bash
sudo apt install tcpdump
```

---

## 🧪 Manual Test

To send a one-time alert to the backend:

```bash
curl -X POST http://localhost:5000/test-alert \
  -H "Content-Type: application/json" \
  -d '{"timestamp":"2025-04-30 18:00:00", "ip":"192.168.0.5", "type":"Test Alert", "attempts":5, "status":"active"}'
```

---

## 💻 Dashboard UI

Live updates for every alert.

Each alert shows:

- Type (e.g., Port Scan)
- IP Address
- Attempt count
- Status (`active`, `blocked`)
- Timestamp

And includes buttons to:

- 🚫 Block IP
- 🔓 Unblock IP

---

## 🔐 IP Blocking

Alerts can be blocked via:

```bash
sudo iptables -A INPUT -s <ip> -j DROP
```

And unblocked:

```bash
sudo iptables -D INPUT -s <ip> -j DROP
```

---

## 📦 API Routes

| Endpoint                  | Method | Description                |
|---------------------------|--------|----------------------------|
| `/alerts`                | GET    | Fetch all alerts           |
| `/test-alert`            | POST   | Send custom alert          |
| `/block/<ip>`            | POST   | Block a suspicious IP      |
| `/unblock/<ip>`          | POST   | Unblock a previously blocked IP |

---

## 🌐 WebSocket

- **Channel**: `/socket.io`
- **Event**: `new_alert`
- **Client**: React connects using `socket.io-client`
- Backend emits real-time updates on new alert arrival.

---

## 🧠 To-Do / Milestones

- [x] SSH brute-force detection
- [x] Port scan detection
- [x] Real-time frontend
- [x] Block/unblock IPs
- [ ] Dashboard analytics (charts, stats)
- [ ] Authentication for admin UI
- [ ] Persistent DB (e.g., SQLite/PostgreSQL)

---

## 🛠️ Developer Notes

- This app is built for local network defense simulations.
- You must run detection scripts with **sudo**.
- Designed for educational and demonstration purposes only.

---

## 🧑‍💻 Author

Made with ❤️ by Brayjin J Antony  
`CSE Cybersecurity | KSR Institute`  
GitHub: [@brayjin](https://github.com/brayjin)

---
