# Real-Time Networking

Last verified: 2026-06-20

## Goal

Learn when to use polling, Server-Sent Events, WebSocket, WebRTC data channels, and WebTransport.

WebTransport is the main new experiment here. It belongs in this repository because it requires platform-level thinking:

- HTTPS and secure contexts
- HTTP/3 server support
- local certificate strategy
- observability for long-lived sessions
- fallback behavior when the browser or network does not support it

## Current WebTransport Notes

- MDN marks WebTransport as Baseline 2026 and newly available since March 2026.
- The API is available only in secure contexts.
- WebTransport connects a browser client to an HTTP/3 server.
- It supports reliable streams and unreliable datagrams.
- It can be available in Web Workers.
- The W3C WebTransport document is still an editor's draft, so this should be treated as a learning experiment rather than a default production choice.

## Comparison

| Technique | Good for | Watch out for |
| --- | --- | --- |
| Polling | simple dashboards, low-frequency updates | latency and repeated request overhead |
| Server-Sent Events | server-to-client event streams | one-way only |
| WebSocket | broad browser support and bidirectional messages | no built-in unreliable datagrams |
| WebRTC data channel | peer-to-peer or media-adjacent data | signaling and NAT complexity |
| WebTransport | HTTP/3 streams, datagrams, low-latency client/server experiments | server support, browser support, certificates, operational complexity |

## Planned Experiment

```text
examples/
  realtime/
    websocket-echo/
    sse-feed/
    webtransport-echo/
docs/
  realtime-networking.md
```

The WebTransport example should include:

- a browser client
- an HTTP/3 WebTransport server
- bidirectional stream echo
- datagram echo
- connection lifecycle logging
- fallback note for WebSocket/SSE

## Definition of Done

- README explains local HTTPS/certificate setup.
- Browser support is checked at runtime with progressive enhancement.
- Example documents stream vs datagram behavior.
- Example includes a fallback decision table.
- Observability notes show connection open, close, errors, and message counts.

## References

- MDN WebTransport: https://developer.mozilla.org/en-US/docs/Web/API/WebTransport
- W3C WebTransport editor's draft: https://w3c.github.io/webtransport/
- Chrome WebTransport guide: https://developer.chrome.com/docs/capabilities/web-apis/webtransport
