# fix.py
import json

input_path = "alerts.json"
output_path = "alerts_fixed.jsonl"  # output will be clean and correct

with open(input_path, "r") as f:
    data = f.read().strip()

try:
    # Case 1: Array of JSON objects
    alerts = json.loads(data)
    assert isinstance(alerts, list)
except Exception:
    # Case 2: Already line-delimited JSON (jsonl)
    print("Already in line-delimited format or malformed JSON array.")
    alerts = []
    for line in data.splitlines():
        try:
            alerts.append(json.loads(line))
        except json.JSONDecodeError as e:
            print(f"❌ Skipping bad line: {line} -> {e}")

# Write clean line-delimited JSON
with open(output_path, "w") as f:
    for alert in alerts:
        f.write(json.dumps(alert) + "\n")

print(f"✅ Fixed alerts saved to: {output_path}")
