import { useEffect, useState } from "react";
import { io } from "socket.io-client";

const socket = io("http://localhost:5000");

function App() {
  const [alerts, setAlerts] = useState([]);
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetchAlerts();

    socket.on("new_alert", (newAlert) => {
      console.log("\u26a1 New alert received:", newAlert);
      setAlerts((prev) => [newAlert, ...prev]);
    });

    return () => socket.disconnect();
  }, []);

  const fetchAlerts = async () => {
    const res = await fetch("http://localhost:5000/alerts");
    const data = await res.json();
    setAlerts(data);
  };

  const blockIP = async (ip) => {
    const res = await fetch(`http://localhost:5000/block/${ip}`, { method: "POST" });
    const data = await res.json();
    setMessage(data.message);
    fetchAlerts();
    setTimeout(() => setMessage(""), 3000);
  };

  const unblockIP = async (ip) => {
    const res = await fetch(`http://localhost:5000/unblock/${ip}`, { method: "POST" });
    const data = await res.json();
    setMessage(data.message);
    fetchAlerts();
    setTimeout(() => setMessage(""), 3000);
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-4">\ud83d\udee1\ufe0f Mini SOC Dashboard</h1>

        {message && (
          <div className="bg-green-600 px-4 py-2 rounded mb-4 shadow-md animate-pulse">
            {message}
          </div>
        )}

        {alerts.length === 0 ? (
          <p className="text-gray-400">No alerts yet.</p>
        ) : (
          <div className="space-y-4">
            {alerts.map((alert, idx) => (
              <div
                key={idx}
                className="bg-gray-800 p-4 rounded shadow hover:shadow-lg transition"
              >
                <p><b>Type:</b> {alert.type}</p>
                <p><b>IP:</b> {alert.ip}</p>
                <p><b>Attempts:</b> {alert.attempts}</p>
                <p><b>Status:</b> {alert.status}</p>
                <p><b>Timestamp:</b> {alert.timestamp}</p>

                {alert.status === "blocked" ? (
                  <button
                    onClick={() => unblockIP(alert.ip)}
                    className="mt-3 bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded"
                  >
                    \ud83d\udd13 Unblock IP
                  </button>
                ) : (
                  <button
                    onClick={() => blockIP(alert.ip)}
                    className="mt-3 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded"
                  >
                    \ud83d\udeab Block IP
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
