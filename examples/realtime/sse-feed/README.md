# SSE Feed (standard library)

A minimal, runnable **Server-Sent Events** lab. A `python3 http.server` streams a
short feed of timestamped JSON events as `text/event-stream`, and a tiny browser
client built on `new EventSource('/events')` appends them to the page. No
frameworks, no `pip install`, no network access at runtime.

This example exercises the repo's named real-time learning target: SSE with an
`EventSource` browser client and a documented polling fallback.

Last verified: 2026-06-21

## What it shows

- The SSE wire format: `event:`, `id:`, `retry:`, and `data: <json>` fields, with
  the **blank line** that terminates (dispatches) each event.
- Correct response headers: `Content-Type: text/event-stream`,
  `Cache-Control: no-cache`, chunked transfer, and `X-Accel-Buffering: no` so a
  fronting NGINX does not buffer the stream.
- An `EventSource` client that listens for named (`tick`) events, reports
  connection state, and **falls back to polling** when `EventSource` is absent.
- An in-process, ephemeral-port test so nothing has to be started by hand.

## Files

| File | Purpose |
| --- | --- |
| `server.py` | `http.server` serving `GET /` (the client) and `GET /events` (the stream). Pure framing helpers (`sse_record`, `event_stream`) are unit-testable. |
| `index.html` | Browser client using `new EventSource('/events')` with a polling fallback branch. |
| `test_sse.py` | `unittest` suite: framing unit tests + an end-to-end HTTP test on an ephemeral port. |

## Run

```bash
# Serve on a fixed port and open the browser client:
python3 examples/realtime/sse-feed/server.py --port 8091
# then open http://127.0.0.1:8091/ in a browser,
# or stream from the terminal:
#   curl -N http://127.0.0.1:8091/events

# Or just print the exact SSE wire bytes and exit (no server):
python3 examples/realtime/sse-feed/server.py --demo
```

The server binds `127.0.0.1`. Pass `--port 0` for an ephemeral port (the chosen
port is printed on startup).

## Test

```bash
python3 examples/realtime/sse-feed/test_sse.py
```

The test starts the server in a background daemon thread on an **ephemeral port**,
reads `/events` with `http.client`, asserts the SSE framing and that every JSON
payload parses, checks the index serves an `EventSource` client, then shuts the
server down. It is non-interactive and exits non-zero on failure.

## How SSE works here

One event on the wire looks like this (note the trailing blank line):

```text
retry: 3000
id: 1
event: tick
data: {"n":1,"message":"event 1 of 5","ts":1781989100.01}

```

- `data:` carries the payload. We serialize JSON onto a single line so it stays in
  one field. Multiple `data:` lines would be joined with `\n` by the browser.
- `id:` becomes `Last-Event-ID`, sent back as a request header when the browser
  auto-reconnects, so the server can resume.
- `retry:` tells the browser how long (ms) to wait before reconnecting.
- `event:` names the event; the client listens with
  `source.addEventListener('tick', ...)`. Without it, the default `message` event
  fires.
- The **blank line** (`\n\n`) is mandatory: it is what dispatches the event.

The browser's `EventSource` reconnects automatically on a dropped connection.
Our demo server closes the stream after a few events, which the client detects via
`readyState === EventSource.CLOSED` and reports as "stream finished".

## Documented fallback (per the repo real-time DoD)

`docs/realtime-networking.md` requires every real-time example to document its
fallback. SSE's fallback is **polling**:

1. Prefer `EventSource('/events')` when `typeof window.EventSource !== 'undefined'`.
2. Otherwise `fetch('/events')` once (or on an interval) and parse the records.
   `index.html` implements exactly this branch.

A production polling fallback would usually hit a dedicated JSON endpoint and poll
on a timer with backoff, rather than re-reading the stream body. The decision
table in `docs/realtime-networking.md` covers when to choose polling, SSE,
WebSocket, or WebTransport.

## Upgrade path

This is a foundation. Swap in the heavier tools later, one concern at a time.

### 1. Put it behind NGINX (the key SSE gotcha: buffering)

NGINX buffers proxied responses by default, which **breaks SSE** (the browser sees
nothing until the buffer flushes or the connection closes). Disable buffering and
keep the connection alive:

```nginx
# /events must NOT be buffered, or the stream is invisible until it closes.
location /events {
    proxy_pass http://127.0.0.1:8091;

    proxy_http_version 1.1;          # keep-alive / streaming
    proxy_set_header Connection "";  # clear "close" so upstream keep-alive works
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

    proxy_buffering off;             # <-- the critical SSE setting
    proxy_cache off;
    chunked_transfer_encoding on;
    proxy_read_timeout 1h;           # long-lived stream
}

location / {
    proxy_pass http://127.0.0.1:8091;
}
```

The server already sends `X-Accel-Buffering: no`, which NGINX honors per-response
even without `proxy_buffering off`, but setting it in config is the explicit,
reviewable form. See `docs/nginx-reverse-proxy.md` and the WebSocket-proxy notes
for the analogous upgrade-header handling.

### 2. Replace the stdlib server with a real async framework

`http.server` is one thread per connection. For many concurrent long-lived
streams, move to an async server while keeping the exact same `text/event-stream`
framing:

- **Starlette / FastAPI** with `StreamingResponse(generator, media_type="text/event-stream")`.
- **aiohttp** with `web.StreamResponse` and `resp.write(...)`.
- Node: `res.writeHead(200, { 'Content-Type': 'text/event-stream' })` and `res.write('data: ...\n\n')`.

The framing in `sse_record()` ports directly to any of these.

### 3. Move past SSE when you need more

| Need | Reach for | Why |
| --- | --- | --- |
| One-way server -> client, easy HTTP/proxy story, auto-reconnect | **SSE** (this example) | Simplest streaming; just HTTP and a text body. One-way only. |
| Two-way, low-latency messages, broad browser support | **WebSocket** | Full duplex over a single upgraded connection. See `examples/realtime/websocket-echo` (planned). Behind NGINX it needs `Upgrade`/`Connection` headers, not `proxy_buffering off`. |
| HTTP/3 streams + unreliable datagrams, lowest latency | **WebTransport** | Newest; needs HTTP/3, secure context, certificates. See `examples/realtime/webtransport-echo` (planned) and `docs/realtime-networking.md`. |
| No native streaming available at all | **Polling** | Universal fallback; higher latency and request overhead. |

## Exercises

1. **Infinite feed + heartbeat.** Make `/events` loop forever instead of stopping
   at `EVENT_COUNT`, and emit an SSE comment line (`: keepalive\n\n`) every ~15s so
   idle proxies do not time the connection out. Confirm `curl -N` keeps printing.
2. **Resume with `Last-Event-ID`.** Read the `Last-Event-ID` request header in
   `do_GET`, and start the feed from `id + 1`. Test it by reconnecting with
   `curl -N -H 'Last-Event-ID: 3' .../events` and asserting it resumes at id 4.
3. **Run it behind NGINX.** Use the config above. First set `proxy_buffering on`
   and watch the stream stall, then flip it `off` and watch events arrive live.
   Write down what you observed.
4. **Add a polling endpoint.** Add `GET /poll` that returns the latest event as
   plain JSON, then change `index.html`'s fallback to poll `/poll` on a timer with
   backoff instead of re-reading the stream. Add a test for `/poll`.
5. **Multiple named event types.** Emit both `tick` and a periodic `stats` event
   (e.g. uptime / event count), and have the client render them in separate lists.
   Extend `test_sse.py` to assert both event names appear.
