# INFRASTRUCTURE — provided by the tutor, do NOT edit.
# Tiny local API that simulates a slow external service.
# Every request takes ~0.3s to respond (network latency simulation).
#
# Run it in its own terminal and leave it running:
#   python server.py
"""Local mock API: GET /models/<n> -> JSON after a 0.3s delay."""

import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DELAY_SECONDS = 0.3
PORT = 8123

MODELS = {
    str(n): {"id": n, "name": f"model-{n}", "context_window": 1000 * (n + 1)}
    for n in range(10)
}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        time.sleep(DELAY_SECONDS)  # simulated latency
        model_id = self.path.rstrip("/").split("/")[-1]
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
    print(f"Mock API listening on http://127.0.0.1:{PORT} (delay {DELAY_SECONDS}s per request)")
    print("Press Ctrl+C to stop.")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
