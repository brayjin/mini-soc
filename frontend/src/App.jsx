import React, { useEffect, useState } from "react";

export default function App() {
  const [alerts, setAlerts] = useState([]);

  // Fetch alerts periodically
  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const res = await fetch("http://localhost:5000/alerts");
        const data = await res.json();
        console.log("Fetched alerts:", data); // debug log

        // Ensure data is an array; fallback to empty array if not
        setAlerts(Array.isArray(data) ? data : []);
      } catch (error) {
        console.error("Failed to fetch alerts:", error);
        setAlerts([]); // fallback to empty array
      }
    };

    fetchAlerts();
    const interval = setInterval(fetchAlerts, 5000); // refresh every 5 sec

    return () => clearInterval(interval);
  }, []);

  // Block or unblock IP (simplified handlers)
  const blockIp = async (ip) => {
    await fetch(`http://localhost:5000/block/${ip}`, { method: "POST" });
  };

  const unblockIp = async (ip) => {
    await fetch(`http://localhost:5000/unblock/${ip}`, { method: "POST" });
  };

  return (
    <div className="min-h-screen bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 text-gray-100 p-8 font-sans">
      <header className="mb-10">
        <h1 className="text-4xl font-extrabold tracking-wide">Mini SOC Dashboard</h1>
        <p className="mt-2 text-gray-400">Real-time Security Alerts & IP Management</p>
      </header>

      <main>
        <table className="w-full table-auto border-collapse border border-gray-700 rounded-lg overflow-hidden shadow-lg">
          <thead className="bg-gray-800 text-gray-300 uppercase text-sm font-semibold">
            <tr>
              <th className="border border-gray-700 p-3 text-left">Timestamp</th>
              <th className="border border-gray-700 p-3 text-left">IP Address</th>
              <th className="border border-gray-700 p-3 text-left">Type</th>
              <th className="border border-gray-700 p-3 text-left">Attempts</th>
              <th className="border border-gray-700 p-3 text-left">Status</th>
              <th className="border border-gray-700 p-3 text-left">Action</th>
            </tr>
          </thead>
          <tbody>
            {(!Array.isArray(alerts) || alerts.length === 0) && (
              <tr>
                <td colSpan="6" className="text-center p-6 text-gray-500">
                  No alerts available
                </td>
              </tr>
            )}
            {Array.isArray(alerts) && alerts.map((alert, idx) => (
              <tr
                key={idx}
                className={`border border-gray-700 hover:bg-gray-700 transition-colors ${
                  alert.status === "blocked" ? "bg-red-900" : "bg-gray-900"
                }`}
              >
                <td className="p-3">{alert.timestamp}</td>
                <td className="p-3 font-mono">{alert.ip}</td>
                <td className="p-3">{alert.type}</td>
                <td className="p-3">{alert.attempts ?? "-"}</td>
                <td
                  className={`p-3 font-semibold ${
                    alert.status === "blocked" ? "text-red-400" : "text-green-400"
                  }`}
                >
                  {alert.status}
                </td>
                <td className="p-3">
                  {alert.status === "blocked" ? (
                    <button
                      onClick={() => unblockIp(alert.ip)}
                      className="px-4 py-1 bg-green-600 rounded hover:bg-green-700 transition"
                    >
                      Unblock
                    </button>
                  ) : (
                    <button
                      onClick={() => blockIp(alert.ip)}
                      className="px-4 py-1 bg-red-600 rounded hover:bg-red-700 transition"
                    >
                      Block
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </main>
    </div>
  );
}
