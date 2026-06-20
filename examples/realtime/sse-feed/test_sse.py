"""Non-interactive tests for the standard-library SSE feed.

Run:

    python3 examples/realtime/sse-feed/test_sse.py

The HTTP test starts the server in a background daemon thread on an EPHEMERAL
port (port 0), connects with http.client, reads the streamed body, then shuts
the server down. No human needs to start a server, and the process exits
non-zero if any assertion fails.
"""

from __future__ import annotations

import json
import os
import sys
import unittest

# Make `import server` work no matter what directory the test is launched from.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import http.client  # noqa: E402

import server  # noqa: E402


class SseFramingTest(unittest.TestCase):
    """Unit tests for the pure framing helpers (no socket involved)."""

    def test_record_ends_with_blank_line(self) -> None:
        record = server.sse_record({"n": 1}).decode("utf-8")
        # The record-terminating blank line is what dispatches an SSE event.
        self.assertTrue(record.endswith("\n\n"))

    def test_record_contains_all_fields(self) -> None:
        record = server.sse_record(
            {"n": 7},
            event_id=7,
            event="tick",
            retry_ms=3000,
        ).decode("utf-8")
        self.assertIn("id: 7", record)
        self.assertIn("event: tick", record)
        self.assertIn("retry: 3000", record)
        self.assertIn('data: {"n":7}', record)

    def test_data_payload_is_single_line_json(self) -> None:
        record = server.sse_record({"a": 1, "b": [1, 2, 3]}).decode("utf-8")
        data_lines = [ln for ln in record.splitlines() if ln.startswith("data:")]
        # Exactly one data line means the JSON did not leak a newline.
        self.assertEqual(len(data_lines), 1)
        parsed = json.loads(data_lines[0][len("data:") :].strip())
        self.assertEqual(parsed, {"a": 1, "b": [1, 2, 3]})

    def test_stream_yields_expected_count(self) -> None:
        chunks = list(server.event_stream(count=3))
        self.assertEqual(len(chunks), 3)


class SseHttpTest(unittest.TestCase):
    """End-to-end test against a real in-process server on an ephemeral port."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.server, cls.thread = server.serve_in_thread(port=0)
        cls.host, cls.port = cls.server.server_address

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def _read_stream(self) -> str:
        conn = http.client.HTTPConnection(self.host, self.port, timeout=10)
        try:
            conn.request("GET", "/events")
            resp = conn.getresponse()
            self.assertEqual(resp.status, 200)
            # The media type is the contract EventSource relies on.
            self.assertEqual(
                resp.getheader("content-type"), "text/event-stream"
            )
            self.assertEqual(resp.getheader("cache-control"), "no-cache")
            # http.client transparently de-chunks the body for us.
            body = resp.read().decode("utf-8")
            return body
        finally:
            conn.close()

    def test_index_serves_eventsource_client(self) -> None:
        conn = http.client.HTTPConnection(self.host, self.port, timeout=10)
        try:
            conn.request("GET", "/")
            resp = conn.getresponse()
            self.assertEqual(resp.status, 200)
            self.assertIn("text/html", resp.getheader("content-type"))
            html = resp.read().decode("utf-8")
            # The browser client must actually use EventSource.
            self.assertIn("new EventSource", html)
            # And it must document a fallback branch.
            self.assertIn("EventSource", html)
            self.assertIn("polling", html.lower())
        finally:
            conn.close()

    def test_event_stream_framing_and_payloads(self) -> None:
        body = self._read_stream()

        # SSE framing: every event ends with a blank line.
        self.assertIn("\n\n", body)
        self.assertIn("retry: ", body)
        self.assertIn("id: 1", body)
        self.assertIn("event: tick", body)

        # Split into records on the blank-line terminator and parse each
        # data payload as JSON.
        records = [r for r in body.split("\n\n") if "data:" in r]
        self.assertEqual(len(records), server.EVENT_COUNT)

        seen_ids = []
        for record in records:
            data_line = next(
                ln for ln in record.splitlines() if ln.startswith("data:")
            )
            payload = json.loads(data_line[len("data:") :].strip())
            # JSON payload must parse and carry the expected fields.
            self.assertIn("n", payload)
            self.assertIn("message", payload)
            self.assertIn("ts", payload)
            id_line = next(
                ln for ln in record.splitlines() if ln.startswith("id:")
            )
            seen_ids.append(int(id_line[len("id:") :].strip()))

        # Event ids are monotonic 1..EVENT_COUNT.
        self.assertEqual(seen_ids, list(range(1, server.EVENT_COUNT + 1)))

    def test_unknown_path_is_404(self) -> None:
        conn = http.client.HTTPConnection(self.host, self.port, timeout=10)
        try:
            conn.request("GET", "/nope")
            resp = conn.getresponse()
            self.assertEqual(resp.status, 404)
            resp.read()
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
