from __future__ import annotations

import argparse
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

started_at = time.time()
requests_total = 0


def payload_for(path: str) -> tuple[int, dict[str, Any] | str, str]:
    global requests_total
    requests_total += 1
    if path == "/healthz":
        return 200, {"status": "ok"}, "application/json"
    if path == "/readyz":
        return 200, {"ready": True, "dependency": "local-memory"}, "application/json"
    if path == "/metrics":
        uptime = time.time() - started_at
        body = f"app_requests_total {requests_total}\napp_uptime_seconds {uptime:.3f}\n"
        return 200, body, "text/plain"
    return 404, {"error": "not found"}, "application/json"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        status, payload, content_type = payload_for(self.path)
        log("request", path=self.path, status=status)
        body = payload if isinstance(payload, str) else json.dumps(payload)
        encoded = body.encode()
        self.send_response(status)
        self.send_header("content-type", content_type)
        self.send_header("content-length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format: str, *args: Any) -> None:
        return


def log(event: str, **fields: Any) -> None:
    print(json.dumps({"event": event, **fields}, sort_keys=True))


def demo() -> None:
    for path in ["/healthz", "/readyz", "/metrics"]:
        status, payload, _ = payload_for(path)
        print(json.dumps({"path": path, "status": status, "payload": payload}, default=str))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()
    if args.demo:
        demo()
        return
    server = ThreadingHTTPServer(("127.0.0.1", 8090), Handler)
    print("listening on http://127.0.0.1:8090")
    server.serve_forever()


if __name__ == "__main__":
    main()

