# Learning Platform Engineering

CI/CD, containers, Kubernetes, NGINX, observability, security, release, and operational engineering for the learning repositories.

Last verified: 2026-06-20

## Runnable Starter Project

Run a tiny observable service before adding Docker, Kubernetes, NGINX, or OpenTelemetry:

```bash
python3 projects/healthcheck-observability/server.py --demo
python3 projects/healthcheck-observability/test_server.py
```

To run the local HTTP service:

```bash
python3 projects/healthcheck-observability/server.py
```

## Why This Repo Exists

Frontend, backend, and AI examples all need the same platform skills:

- CI that catches breakage
- repeatable local environments
- safe secret handling
- dependency and supply-chain hygiene
- observable services
- real-time networking experiments
- reverse proxy and edge-routing basics
- simple deployment notes
- runbooks for failures

This repo keeps those cross-cutting skills out of app-specific repos.

## How To Use This Repo

Use this as the operations notebook for the other learning repositories. A good study loop is:

1. pick one small application from another repo
2. add CI so build/test/check is repeatable
3. put a local service or reverse proxy in front of it
4. add logs, metrics, traces, and health checks
5. write the release, rollback, and failure notes

The point is not to build a production platform. The point is to understand the smallest useful operational layer around an application.

## Learning Path

1. GitHub Actions CI
2. Docker and Compose
3. Kubernetes concepts
4. NGINX reverse proxy, static files, TLS, load balancing, WebSocket proxying
5. OpenTelemetry traces, metrics, logs
6. Real-time networking: SSE, WebSocket, and WebTransport
7. OWASP Top 10 and secure coding basics
8. dependency security and SBOM basics
9. release and rollback checklist
10. runbooks and incident notes

## Planned Structure

```text
examples/
  github-actions/
  docker-compose-postgres/
  kubernetes-basic-web-api/
  nginx-reverse-proxy/
  realtime/
docs/
  2026-learning-items.md
  nginx-reverse-proxy.md
  realtime-networking.md
  repository-profile.md
  security-checklist.md
  release-checklist.md
  runbook-template.md
```

## What Belongs Here

- CI/CD workflow templates
- Docker, Compose, and Kubernetes learning examples
- NGINX and reverse proxy notes
- OpenTelemetry and logging/metrics/traces notes
- release checklists, runbooks, and operational templates
- defensive security checklist items that apply to every repo

## What Belongs Elsewhere

- P2P, WebRTC, and libp2p protocol mechanics belong here under realtime networking notes
- ethical hacking labs belong in `learning-security-labs`
- app-specific framework code belongs in frontend/backend/AI repos
- Bazel and Nix experiments belong in `learning-build-systems`

## Repository Profile

See [docs/repository-profile.md](docs/repository-profile.md) for GitHub description, topics, public safety notes, and first milestones.
