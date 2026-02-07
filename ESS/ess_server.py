"""
ESS (End System Server)

A server that listens for sensor data from ES clients via a REST API
and prints the received JSON data.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys

HOST = "0.0.0.0"
PORT = 5050


class ESSRequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        if self.path == "/api/sensor-data":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                sensor_data = json.loads(body)
                print("\n--- Received Sensor Data ---")
                print(json.dumps(sensor_data, indent=2))
                print("----------------------------\n")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok"}).encode())
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": "Invalid JSON"}).encode())
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": "Not found"}).encode())

    def log_message(self, format, *args):
        # Suppress default HTTP request logging to keep output clean
        pass


def main():
    server = HTTPServer((HOST, PORT), ESSRequestHandler)
    print(f"ESS Server listening on {HOST}:{PORT}")
    print("Waiting for sensor data...\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nESS Server shutting down.")
        server.server_close()
        sys.exit(0)


if __name__ == "__main__":
    main()
