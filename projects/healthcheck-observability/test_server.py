from server import payload_for


def test_health_payload() -> None:
    status, payload, content_type = payload_for("/healthz")
    assert status == 200
    assert payload == {"status": "ok"}
    assert content_type == "application/json"


def test_metrics_payload_is_prometheus_shaped() -> None:
    status, payload, content_type = payload_for("/metrics")
    assert status == 200
    assert isinstance(payload, str)
    assert "app_requests_total" in payload
    assert content_type == "text/plain"


if __name__ == "__main__":
    test_health_payload()
    test_metrics_payload_is_prometheus_shaped()
    print("ok")

