# INFRASTRUCTURE — provided by the tutor, do NOT edit.
# Local API that simulates a FLAKY external service:
#   - GET /models/3 -> HTTP 500 after the normal delay (server-side error)
#   - GET /models/7 -> hangs for 10s before answering (stuck server)
#   - every other id in 0..9 -> HTTP 200 with JSON after ~0.3s
#
# Run it in its own terminal and leave it running:
#   python flaky_server.py
"""Local flaky mock API: GET /models/<n> with one error and one hang."""

import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DELAY_SECONDS = 0.3
HANG_SECONDS = 10.0
PORT = 8124

ERROR_ID = "3"
HANG_ID = "7"

MODELS = {
    str(n): {"id": n, "name": f"model-{n}", "context_window": 1000 * (n + 1)}
    for n in range(10)
}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        model_id = self.path.rstrip("/").split("/")[-1]

        if model_id == HANG_ID:
            time.sleep(HANG_SECONDS)  # simulated stuck server
        else:
            time.sleep(DELAY_SECONDS)  # simulated normal latency

        if model_id == ERROR_ID:
            self.send_response(500)
            self.end_headers()
            return

        model = MODELS.get(model_id)
        if model is None:
            self.send_response(404)
            self.end_headers()
            return

        body = json.dumps(model).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):  # silence per-request logging
        pass


if __name__ == "__main__":
    print(f"Flaky mock API on http://127.0.0.1:{PORT}")
    print(f"  /models/{ERROR_ID} -> 500, /models/{HANG_ID} -> hangs {HANG_SECONDS}s, rest -> 200")
    print("Press Ctrl+C to stop.")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
