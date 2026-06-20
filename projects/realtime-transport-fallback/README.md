# Realtime Transport Fallback

Learn where WebTransport fits before adding an HTTP/3 server.

This lab chooses the best available realtime transport from a small capability object:

1. WebTransport when the browser supports it and the page is in a secure context.
2. WebSocket for broad bidirectional realtime support.
3. Server-Sent Events for server-to-client streams.
4. Long polling as the last compatible fallback.

## Run

```bash
node projects/realtime-transport-fallback/transport.test.mjs
node projects/realtime-transport-fallback/transport.mjs
```

You can also open `index.html` directly in a browser to see the detected transport.

## Why This Exists

Real WebTransport experiments need HTTPS, HTTP/3, and server support. This project keeps
the decision logic runnable first, then leaves room to add a real WebTransport server later.
