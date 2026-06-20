# Network Protocol Lab

Network programming gets easier when the failure modes are visible. This lab is
socket-free and dependency-free, but it models the real rules you need before
writing TCP, UDP, HTTP, WebSocket, WebRTC, or WebTransport code.

## Run

```bash
python3 projects/network-protocol-lab/protocol.py
python3 projects/network-protocol-lab/test_protocol.py
```

## What It Teaches

- TCP is a byte stream, so application messages need framing.
- UDP preserves datagram boundaries, but delivery and ordering are not promised.
- timeouts, retries, and backoff must be explicit.
- HTTP retries need idempotency keys when the operation has side effects.
- proxy boundaries should preserve the request information the app needs.

## Exercises

1. Change the maximum frame size and assert oversized frames are rejected.
2. Add jitter to the retry schedule and keep the tests deterministic by injecting
   a fake random source.
3. Extend `IdempotencyStore` to expire cached responses after a TTL.
4. Add a route table that distinguishes public, internal, and admin upstreams.
