from protocol import (
    HttpRequest,
    IdempotencyStore,
    ProtocolError,
    backoff_delays_ms,
    encode_frame,
    feed_frames,
    forwarded_headers,
    stop_and_wait_schedule,
)


def assert_raises(fn, expected) -> None:
    try:
        fn()
    except expected:
        return
    raise AssertionError(f"expected {expected.__name__}")


def test_tcp_framing() -> None:
    buffer = bytearray()
    encoded = encode_frame(b"alpha") + encode_frame(b"beta")
    assert feed_frames(buffer, encoded[:3]) == []
    assert feed_frames(buffer, encoded[3:8]) == []
    assert feed_frames(buffer, encoded[8:]) == [b"alpha", b"beta"]
    assert buffer == bytearray()


def test_oversized_frame_rejected() -> None:
    assert_raises(lambda: encode_frame(b"x" * (16 * 1024 + 1)), ProtocolError)


def test_backoff() -> None:
    assert backoff_delays_ms(6, base_ms=100, cap_ms=500) == [100, 200, 400, 500, 500, 500]


def test_stop_and_wait_retransmits_after_lost_ack() -> None:
    schedule = stop_and_wait_schedule(["one", "two"], lost_acks={1: 2})
    assert [(item.seq, item.attempt, item.timeout_ms) for item in schedule] == [
        (1, 1, 100),
        (1, 2, 200),
        (1, 3, 400),
        (2, 1, 100),
    ]


def test_idempotency_store_replays_same_request() -> None:
    store = IdempotencyStore()
    request = HttpRequest("POST", "/orders", '{"sku":"book"}', idempotency_key="order-1")
    first = store.process(request)
    second = store.process(request)
    assert first.status == 201
    assert second.status == 201
    assert second.replayed is True


def test_idempotency_store_rejects_key_reuse_for_different_body() -> None:
    store = IdempotencyStore()
    store.process(HttpRequest("POST", "/orders", '{"sku":"book"}', idempotency_key="order-1"))
    conflict = store.process(HttpRequest("POST", "/orders", '{"sku":"pen"}', idempotency_key="order-1"))
    assert conflict.status == 409


def test_forwarded_headers() -> None:
    headers = forwarded_headers("203.0.113.10", "example.test")
    assert headers["x-forwarded-for"] == "203.0.113.10"
    assert headers["x-forwarded-proto"] == "https"
    assert headers["host"] == "example.test"


def main() -> None:
    test_tcp_framing()
    test_oversized_frame_rejected()
    test_backoff()
    test_stop_and_wait_retransmits_after_lost_ack()
    test_idempotency_store_replays_same_request()
    test_idempotency_store_rejects_key_reuse_for_different_body()
    test_forwarded_headers()
    print("ok")


if __name__ == "__main__":
    main()
