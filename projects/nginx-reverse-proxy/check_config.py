from __future__ import annotations

from pathlib import Path


def main() -> None:
    text = Path(__file__).with_name("nginx.conf").read_text()
    required = ["listen 8088", "location /healthz", "proxy_pass", "x-forwarded-for"]
    missing = [item for item in required if item not in text]
    if missing:
        raise SystemExit(f"missing nginx concepts: {missing}")
    print("ok")


if __name__ == "__main__":
    main()

