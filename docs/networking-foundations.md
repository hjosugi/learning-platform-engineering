# Networking Foundations

Last verified: 2026-06-21

## Study Order

1. IP addressing, loopback, private ranges, and ports
2. DNS lookup, TTL, and host headers
3. TCP byte streams, connection lifecycle, and framing
4. UDP datagrams, loss, ordering, and retries
5. HTTP request/response, status codes, headers, and idempotency
6. TLS certificates, SNI, and secure contexts
7. reverse proxies: Host, X-Forwarded-For, X-Forwarded-Proto
8. load balancing, health checks, and connection draining
9. long-lived connections: SSE and WebSocket
10. WebRTC/WebTransport and fallback strategy
11. NAT, firewalls, and local-only lab boundaries
12. observability: connection counts, latency, timeouts, retries, and errors

## Design Checklist

- What is the message boundary?
- What timeout applies to connect, read, write, and idle?
- Is retry safe, and is the operation idempotent?
- What happens when a proxy retries or buffers the request?
- Which headers must be preserved across a reverse proxy?
- What metrics prove the connection is healthy?
- What is the fallback when the preferred transport is unavailable?

## Labs

- `projects/network-protocol-lab`: framing, retry, idempotency, proxy headers
- `examples/realtime/sse-feed`: one-way browser event stream
- `projects/realtime-transport-fallback`: browser transport selection
- `projects/p2p-udp-gossip`: local UDP peer messaging
- `projects/nginx-reverse-proxy`: reverse proxy config checks
