"""Server-Sent Events (SSE) feed using only the Python standard library.

This is a foundation example: no Flask, no Starlette, no aiohttp, no extra
packages. It uses `http.server` so it runs with python3 alone. The "Upgrade
path" in README.md explains how to move this behind NGINX and how SSE compares
to WebSocket and WebTransport.

Two routes are served:

    GET /         -> index.html, a browser client built on `new EventSource(...)`
    GET /events   -> a streaming `text/event-stream` response with proper SSE
                     framing (event id, event name, retry hint, and
                     `data: <json>\\n\\n` records), then the stream closes.

SSE wire format (per the WHATWG HTML "Server-sent events" section):

    retry: 3000\\n        # optional: client reconnect backoff in ms
    id: 1\\n              # optional: becomes Last-Event-ID on reconnect
    event: tick\\n        # optional: custom event name (default is "message")
    data: {"n": 1}\\n     # the payload; multiple data: lines are joined by "\\n"
    \\n                   # a BLANK line terminates one event ("dispatch")

The blank line is the most important part: an event is only dispatched to the
browser when the parser sees the record-terminating empty line.
"""

from __future__ import annotations

import argparse
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Iterator

# How many events the demo stream pushes before it closes. Kept small so the
# example (and the test) finish quickly; a real feed would loop indefinitely.
EVENT_COUNT = 5

# Reconnect backoff hint sent to the browser. EventSource reconnects on its own
# when the connection drops; `retry:` tells it how long to wait first.
RETRY_MS = 3000

# Delay between events. Small so the demo is snappy but still visibly streamed.
EVENT_INTERVAL_SECONDS = 0.2


def sse_record(
    data: dict[str, Any],
    *,
    event_id: int | None = None,
    event: str | None = None,
    retry_ms: int | None = None,
) -> bytes:
    """Frame a single SSE event as raw bytes ready to write to the socket.

    The JSON payload is serialized onto a single line (no embedded newlines),
    which keeps it inside one `data:` field. The trailing blank line is what
    actually dispatches the event in the browser.
    """
    lines: list[str] = []
    if retry_ms is not None:
        lines.append(f"retry: {retry_ms}")
    if event_id is not None:
        lines.append(f"id: {event_id}")
    if event is not None:
        lines.append(f"event: {event}")
    # json.dumps without indentation guarantees a single physical line.
    lines.append(f"data: {json.dumps(data, separators=(',', ':'))}")
    # Join the fields with "\n" and end the record with the mandatory blank
    # line, i.e. the record ends in "\n\n".
    return ("\n".join(lines) + "\n\n").encode("utf-8")


def event_stream(count: int = EVENT_COUNT) -> Iterator[bytes]:
    """Yield framed SSE bytes for a short, timestamped JSON feed.

    Yielding bytes (instead of writing directly) keeps the framing logic pure
    and unit-testable independently of any socket.
    """
    for n in range(1, count + 1):
        payload = {
            "n": n,
            "message": f"event {n} of {count}",
            "ts": time.time(),
        }
        # The first record also carries the retry hint and a named event so the
        # client can distinguish "tick" events from the default "message".
        yield sse_record(
            payload,
            event_id=n,
            event="tick",
            retry_ms=RETRY_MS if n == 1 else None,
        )
        time.sleep(EVENT_INTERVAL_SECONDS)


def index_html() -> bytes:
    """Read the co-located browser client so server.py and index.html stay in sync."""
    import os

    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "index.html"), "rb") as fh:
        return fh.read()


class Handler(BaseHTTPRequestHandler):
    # HTTP/1.1 keeps the connection open so the streamed response is read
    # incrementally rather than only after the socket closes.
    protocol_version = "HTTP/1.1"

    def do_GET(self) -> None:
        # Strip any query string before routing.
        path = self.path.split("?", 1)[0]
        if path == "/" or path == "/index.html":
            self._serve_index()
        elif path == "/events":
            self._serve_events()
        else:
            self._serve_not_found()

    def _serve_index(self) -> None:
        body = index_html()
        self.send_response(200)
        self.send_header("content-type", "text/html; charset=utf-8")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_events(self) -> None:
        self.send_response(200)
        # The media type MUST be text/event-stream for EventSource to parse it.
        self.send_header("content-type", "text/event-stream")
        # Disable caching so proxies and the browser never replay a stale stream.
        self.send_header("cache-control", "no-cache")
        # Tell NGINX (if present) not to buffer this response; see README.
        self.send_header("x-accel-buffering", "no")
        # We do not know the length up front, so stream with chunked framing.
        self.send_header("transfer-encoding", "chunked")
        self.end_headers()
        try:
            for chunk in event_stream():
                self._write_chunk(chunk)
            # Terminate the chunked body cleanly.
            self._end_chunks()
        except (BrokenPipeError, ConnectionResetError):
            # The browser closed the tab / EventSource.close() was called.
            # This is normal for SSE and not an error worth logging loudly.
            log("client_disconnected", path=self.path)

    def _serve_not_found(self) -> None:
        body = json.dumps({"error": "not found"}).encode("utf-8")
        self.send_response(404)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _write_chunk(self, data: bytes) -> None:
        """Write one HTTP/1.1 chunked-transfer-encoding chunk."""
        self.wfile.write(f"{len(data):X}\r\n".encode("ascii"))
        self.wfile.write(data)
        self.wfile.write(b"\r\n")
        self.wfile.flush()

    def _end_chunks(self) -> None:
        """Write the zero-length terminating chunk."""
        self.wfile.write(b"0\r\n\r\n")
        self.wfile.flush()

    def log_message(self, format: str, *args: Any) -> None:
        # Silence the default stderr access log; we emit structured logs instead.
        return


def log(event: str, **fields: Any) -> None:
    print(json.dumps({"event": event, **fields}, sort_keys=True))


def make_server(port: int = 0) -> ThreadingHTTPServer:
    """Build a server bound to 127.0.0.1.

    Pass port=0 to bind an ephemeral port; read the chosen port back from
    `server.server_address[1]`. The test uses this so it never races for a
    fixed port.
    """
    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def serve_in_thread(port: int = 0) -> tuple[ThreadingHTTPServer, threading.Thread]:
    """Start the server in a daemon thread and return (server, thread).

    Used by the test harness for an in-process server with no external setup.
    """
    server = make_server(port)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def main() -> None:
    parser = argparse.ArgumentParser(description="Standard-library SSE feed.")
    parser.add_argument(
        "--port",
        type=int,
        default=8091,
        help="Port to bind (default 8091; use 0 for an ephemeral port).",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Print the framed SSE bytes to stdout and exit (no server).",
    )
    args = parser.parse_args()

    if args.demo:
        for chunk in event_stream():
            # Show the exact wire bytes a browser would receive.
            print(chunk.decode("utf-8"), end="")
        return

    server = make_server(args.port)
    host, port = server.server_address[0], server.server_address[1]
    print(f"listening on http://{host}:{port}")
    print(f"open http://{host}:{port}/ in a browser, or curl http://{host}:{port}/events")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
