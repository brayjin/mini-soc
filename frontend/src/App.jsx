import React, { useEffect, useState } from "react";

const API_URL = "http://localhost:5000";

export default function App() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchAlerts = async () => {
    try {
      const res = await fetch(`${API_URL}/alerts`);

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data = await res.json();

      setAlerts(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Failed to fetch alerts:", err);
      setAlerts([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();

    const interval = setInterval(fetchAlerts, 5000);

    return () => clearInterval(interval);
  }, []);

  const blockIp = async (ip) => {
    try {
      const res = await fetch(
        `${API_URL}/block/${ip}`,
        {
          method: "POST",
        }
      );

      const data = await res.json();

      console.log(data);

      await fetchAlerts();
    } catch (err) {
      console.error(err);
    }
  };

  const unblockIp = async (ip) => {
    try {
      const res = await fetch(
        `${API_URL}/unblock/${ip}`,
        {
          method: "POST",
        }
      );

      const data = await res.json();

      console.log(data);

      await fetchAlerts();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-8">
      <div className="max-w-7xl mx-auto">

        <div className="mb-8">
          <h1 className="text-4xl font-bold">
            Mini SOC Dashboard
          </h1>

          <p className="text-gray-400 mt-2">
            Real-time Security Monitoring
          </p>
        </div>

        <div className="mb-6 flex gap-4">

          <div className="bg-gray-900 p-4 rounded-lg border border-gray-800">
            <div className="text-gray-400 text-sm">
              Total Alerts
            </div>

            <div className="text-3xl font-bold">
              {alerts.length}
            </div>
          </div>

          <div className="bg-gray-900 p-4 rounded-lg border border-gray-800">
            <div className="text-gray-400 text-sm">
              Blocked
            </div>

            <div className="text-3xl font-bold text-red-400">
              {
                alerts.filter(
                  a => a.status === "blocked"
                ).length
              }
            </div>
          </div>

        </div>

        <div className="overflow-x-auto">

          <table className="w-full border border-gray-800">

            <thead>
              <tr className="bg-gray-900">

                <th className="p-3 text-left">
                  Timestamp
                </th>

                <th className="p-3 text-left">
                  IP
                </th>

                <th className="p-3 text-left">
                  Type
                </th>

                <th className="p-3 text-left">
                  Attempts
                </th>

                <th className="p-3 text-left">
                  Status
                </th>

                <th className="p-3 text-left">
                  Action
                </th>

              </tr>
            </thead>

            <tbody>

              {loading && (
                <tr>
                  <td
                    colSpan="6"
                    className="p-8 text-center"
                  >
                    Loading...
                  </td>
                </tr>
              )}

              {!loading &&
                alerts.length === 0 && (
                  <tr>
                    <td
                      colSpan="6"
                      className="p-8 text-center text-gray-500"
                    >
                      No alerts found
                    </td>
                  </tr>
                )}

              {alerts.map((alert) => (

                <tr
                  key={
                    alert.id ??
                    `${alert.ip}-${alert.timestamp}`
                  }
                  className="border-t border-gray-800"
                >

                  <td className="p-3">
                    {alert.timestamp}
                  </td>

                  <td className="p-3 font-mono">
                    {alert.ip}
                  </td>

                  <td className="p-3">
                    {alert.type}
                  </td>

                  <td className="p-3">
                    {alert.attempts ?? "-"}
                  </td>

                  <td className="p-3">

                    <span
                      className={
                        alert.status === "blocked"
                          ? "text-red-400"
                          : "text-green-400"
                      }
                    >
                      {alert.status}
                    </span>

                  </td>

                  <td className="p-3">

                    {alert.status === "blocked" ? (

                      <button
                        onClick={() =>
                          unblockIp(alert.ip)
                        }
                        className="bg-green-600 hover:bg-green-700 px-3 py-1 rounded"
                      >
                        Unblock
                      </button>

                    ) : (

                      <button
                        onClick={() =>
                          blockIp(alert.ip)
                        }
                        className="bg-red-600 hover:bg-red-700 px-3 py-1 rounded"
                      >
                        Block
                      </button>

                    )}

                  </td>

                </tr>

              ))}

            </tbody>

          </table>

        </div>
      </div>
    </div>
  );
}