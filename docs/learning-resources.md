# Further learning resources

Last verified: 2026-06-21

Curated, primary-source references for this repo's named real-time networking
target: **Server-Sent Events (`text/event-stream`) with an `EventSource` browser
client and a documented fallback**, plus the adjacent transports it is compared
against (WebSocket, WebTransport) and the NGINX edge concerns for streaming.

## Server-Sent Events and EventSource

- **WHATWG HTML Standard — Server-sent events** — https://html.spec.whatwg.org/multipage/server-sent-events.html
  The normative specification for the `text/event-stream` wire format, the
  `EventSource` interface, event dispatch on the blank line, `id:`/`retry:`/`event:`
  fields, and `Last-Event-ID` reconnection. This is the source of truth for the
  framing in `server.py`.
- **MDN — Using server-sent events** — https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events
  Practical, example-driven guide to building an SSE server and `EventSource`
  client, including event naming, reconnection, and closing streams.
- **MDN — EventSource interface** — https://developer.mozilla.org/en-US/docs/Web/API/EventSource
  Reference for the client API used in `index.html`: constructor, `readyState`,
  `open`/`message`/`error` events, and `withCredentials`.

## Python standard library (how this example is built)

- **Python docs — `http.server`** — https://docs.python.org/3/library/http.server.html
  `BaseHTTPRequestHandler` and `ThreadingHTTPServer`, the request lifecycle, and
  header/body writing used by the stdlib server.
- **Python docs — `http.client`** — https://docs.python.org/3/library/http.client.html
  The low-level HTTP client the test uses to read the streamed response and assert
  the SSE framing.

## Comparison transports (the SSE alternatives)

- **MDN — WebSocket API** — https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API
  Full-duplex alternative to SSE; the right choice when the client must also send
  messages. Compared in the README's transport table.
- **WHATWG — WebSocket (HTML Standard)** — https://html.spec.whatwg.org/multipage/web-sockets.html
  Normative WebSocket browser API (paired with the IETF protocol below).
- **MDN — WebTransport API** — https://developer.mozilla.org/en-US/docs/Web/API/WebTransport
  HTTP/3-based streams and datagrams; the lowest-latency, newest option, requiring
  secure contexts and HTTP/3. Tracked in `docs/realtime-networking.md`.
- **W3C — WebTransport editor's draft** — https://w3c.github.io/webtransport/
  The evolving WebTransport specification; treat as experimental.

## Standards bodies (protocols underneath)

- **IETF Datatracker** — https://datatracker.ietf.org/
  Canonical home for the HTTP, WebSocket (RFC 6455), HTTP/3 (RFC 9114), and QUIC
  (RFC 9000) specifications that these transports run on. Prefer searching here
  over guessing RFC URLs.

## Edge / reverse proxy for streaming

- **NGINX documentation** — https://nginx.org/en/docs/
  Reverse-proxy reference. For SSE the key directive is `proxy_buffering off`
  (and/or honoring `X-Accel-Buffering: no`) so the stream is not buffered. See
  also `docs/nginx-reverse-proxy.md` in this repo.
