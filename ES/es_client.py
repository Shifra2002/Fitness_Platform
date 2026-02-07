"""
ES (End System)

A CLI client that simulates sensors attached to an End System.
When a user is detected (ES_ID entered), the ES periodically reads
sensors and sends the data to the ESS server.

Sensors simulated: heart_rate, blood_oxygen, body_temperature
"""

import json
import random
import threading
import time
import urllib.request
import urllib.error
import sys
from datetime import datetime, timezone

ESS_URL = "http://localhost:5050/api/sensor-data"
SEND_INTERVAL_SECONDS = 10

SENSORS = [
    {"name": "heart_rate", "min": 60, "max": 100, "unit": "bpm"},
    {"name": "blood_oxygen", "min": 94, "max": 100, "unit": "%"},
    {"name": "body_temperature", "min": 36.1, "max": 37.2, "unit": "°C"},
]


def read_sensors(es_id):
    """Simulate reading all sensors and return a JSON-compatible list."""
    timestamp = datetime.now(timezone.utc).isoformat()
    readings = []
    for sensor in SENSORS:
        value = round(random.uniform(sensor["min"], sensor["max"]), 1)
        readings.append({
            "sensor_name": sensor["name"],
            "ES_ID": es_id,
            "timestamp": timestamp,
            "value": value,
            "unit": sensor["unit"],
        })
    return readings


def send_data(sensor_data):
    """Send sensor data to the ESS server."""
    payload = json.dumps(sensor_data).encode()
    req = urllib.request.Request(
        ESS_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        print(f"  [Error] Could not reach ESS: {e}")
        return False


def sensor_loop(es_id, stop_event):
    """Periodically read sensors and send data until stopped."""
    while not stop_event.is_set():
        readings = read_sensors(es_id)
        print(f"  Sending {len(readings)} sensor readings...")
        send_data(readings)
        stop_event.wait(SEND_INTERVAL_SECONDS)


def main():
    print("=== ES (End System) Client ===")
    print(f"Sensor send interval: {SEND_INTERVAL_SECONDS}s")
    print(f"ESS target: {ESS_URL}\n")

    es_id = input("Enter ES_ID to start (or 'quit' to exit): ").strip()
    if not es_id or es_id.lower() == "quit":
        print("Exiting.")
        sys.exit(0)

    print(f"\nUser detected on ES '{es_id}'. Starting sensor readings.")
    print("Type 'stop' and press Enter to stop and exit.\n")

    stop_event = threading.Event()
    worker = threading.Thread(target=sensor_loop, args=(es_id, stop_event), daemon=True)
    worker.start()

    try:
        while True:
            cmd = input()
            if cmd.strip().lower() == "stop":
                break
    except (KeyboardInterrupt, EOFError):
        pass

    print("\nStopping sensor readings...")
    stop_event.set()
    worker.join(timeout=3)
    print("ES client exited.")


if __name__ == "__main__":
    main()
