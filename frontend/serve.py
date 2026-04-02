#!/usr/bin/env python3
"""Simple static + API proxy server for the frontend."""
import http.server
import urllib.request
import urllib.error
import os
import sys

DIST_DIR = os.path.join(os.path.dirname(__file__), "dist")
BACKEND = "http://localhost:8000"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5173


class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIST_DIR, **kwargs)

    def do_GET(self):
        if self.path.startswith("/api/"):
            self._proxy()
        else:
            # SPA fallback: serve index.html for unknown paths
            if not os.path.exists(os.path.join(DIST_DIR, self.path.lstrip("/"))):
                self.path = "/index.html"
            super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/"):
            self._proxy()
        else:
            self.send_error(404)

    def _proxy(self):
        target = BACKEND + self.path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else None

        headers = {
            k: v for k, v in self.headers.items()
            if k.lower() not in ("host", "content-length")
        }
        if body:
            headers["Content-Length"] = str(len(body))

        req = urllib.request.Request(target, data=body, headers=headers, method=self.command)
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                self.send_response(resp.status)
                for k, v in resp.headers.items():
                    if k.lower() in ("transfer-encoding",):
                        continue
                    # Ensure JSON/text responses include charset=utf-8
                    if k.lower() == "content-type" and "charset" not in v.lower() and (
                        "json" in v or "text/" in v or "event-stream" in v
                    ):
                        v = v + "; charset=utf-8"
                    self.send_header(k, v)
                self.end_headers()
                # Stream response (important for SSE)
                while True:
                    chunk = resp.read(4096)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    self.wfile.flush()
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            self.send_error(502, str(e))

    def log_message(self, fmt, *args):
        print(f"[{self.address_string()}] {fmt % args}")


if __name__ == "__main__":
    os.chdir(DIST_DIR)
    server = http.server.HTTPServer(("", PORT), ProxyHandler)
    print(f"✓ Serving on http://localhost:{PORT}")
    print(f"  Static files: {DIST_DIR}")
    print(f"  API proxy: /api/* → {BACKEND}")
    server.serve_forever()
