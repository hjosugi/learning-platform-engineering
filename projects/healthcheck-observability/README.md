# Healthcheck Observability

A local service that exposes health, readiness, metrics, and JSON logs.

## Demo

```bash
python3 projects/healthcheck-observability/server.py --demo
```

## Run Server

```bash
python3 projects/healthcheck-observability/server.py
```

Then call:

```bash
curl http://localhost:8090/healthz
curl http://localhost:8090/readyz
curl http://localhost:8090/metrics
```

