from __future__ import annotations

from pathlib import Path


def main() -> None:
    text = Path(__file__).with_name("ci.yml").read_text()
    required = ["actions/checkout@v4", "actions/setup-python@v5", "python3 projects/healthcheck-observability/test_server.py"]
    missing = [item for item in required if item not in text]
    if missing:
        raise SystemExit(f"missing workflow concepts: {missing}")
    print("ok")


if __name__ == "__main__":
    main()

