from __future__ import annotations

import json
import struct
from dataclasses import asdict, dataclass
from typing import Iterable


MAX_FRAME_BYTES = 16 * 1024


class ProtocolError(ValueError):
    pass


def encode_frame(payload: bytes) -> bytes:
    if len(payload) > MAX_FRAME_BYTES:
        raise ProtocolError("frame is too large")
    return struct.pack("!I", len(payload)) + payload


def feed_frames(buffer: bytearray, incoming: bytes) -> list[bytes]:
    buffer.extend(incoming)
    frames: list[bytes] = []

    while True:
        if len(buffer) < 4:
            return frames
        (size,) = struct.unpack("!I", buffer[:4])
        if size > MAX_FRAME_BYTES:
            raise ProtocolError("frame is too large")
        if len(buffer) < 4 + size:
            return frames
        frames.append(bytes(buffer[4 : 4 + size]))
        del buffer[: 4 + size]


def backoff_delays_ms(attempts: int, *, base_ms: int = 100, cap_ms: int = 2000) -> list[int]:
    if attempts < 0:
        raise ValueError("attempts must not be negative")
    if base_ms <= 0 or cap_ms <= 0:
        raise ValueError("base and cap must be positive")
    return [min(base_ms * (2**attempt), cap_ms) for attempt in range(attempts)]


@dataclass(frozen=True)
class DatagramSend:
    seq: int
    payload: str
    attempt: int
    timeout_ms: int


def stop_and_wait_schedule(payloads: Iterable[str], lost_acks: dict[int, int] | None = None) -> list[DatagramSend]:
    losses = dict(lost_acks or {})
    sends: list[DatagramSend] = []

    for seq, payload in enumerate(payloads, start=1):
        attempt = 0
        while True:
            timeout = backoff_delays_ms(attempt + 1)[-1]
            sends.append(DatagramSend(seq=seq, payload=payload, attempt=attempt + 1, timeout_ms=timeout))
            if losses.get(seq, 0) <= 0:
                break
            losses[seq] -= 1
            attempt += 1

    return sends


@dataclass(frozen=True)
class HttpRequest:
    method: str
    path: str
    body: str
    idempotency_key: str | None = None


@dataclass(frozen=True)
class HttpResponse:
    status: int
    body: str
    replayed: bool = False


class IdempotencyStore:
    def __init__(self) -> None:
        self._responses: dict[str, tuple[str, HttpResponse]] = {}

    def process(self, request: HttpRequest) -> HttpResponse:
        if request.method.upper() in {"GET", "HEAD"}:
            return HttpResponse(status=200, body=f"read {request.path}")

        if request.idempotency_key is None:
            return HttpResponse(status=201, body=f"created {request.path}")

        fingerprint = f"{request.method.upper()} {request.path} {request.body}"
        cached = self._responses.get(request.idempotency_key)
        if cached is not None:
            cached_fingerprint, cached_response = cached
            if cached_fingerprint != fingerprint:
                return HttpResponse(status=409, body="idempotency key reused with different request")
            return HttpResponse(status=cached_response.status, body=cached_response.body, replayed=True)

        response = HttpResponse(status=201, body=f"created {request.path}")
        self._responses[request.idempotency_key] = (fingerprint, response)
        return response


def forwarded_headers(client_ip: str, host: str, proto: str = "https") -> dict[str, str]:
    return {
        "host": host,
        "x-forwarded-for": client_ip,
        "x-forwarded-proto": proto,
    }


def demo() -> dict[str, object]:
    buffer = bytearray()
    encoded = encode_frame(b"hello") + encode_frame(b"world")
    first = feed_frames(buffer, encoded[:7])
    second = feed_frames(buffer, encoded[7:])

    store = IdempotencyStore()
    req = HttpRequest("POST", "/jobs", '{"name":"demo"}', idempotency_key="job-1")

    return {
        "tcp_framing": {
            "first_read": [item.decode() for item in first],
            "second_read": [item.decode() for item in second],
        },
        "udp_retries": [asdict(item) for item in stop_and_wait_schedule(["a", "b"], lost_acks={1: 1})],
        "http_idempotency": [asdict(store.process(req)), asdict(store.process(req))],
        "proxy_headers": forwarded_headers("203.0.113.10", "example.test"),
    }


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2))
