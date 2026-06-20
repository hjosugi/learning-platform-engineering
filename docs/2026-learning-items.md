# 2026 Learning Items: Platform Engineering

Last verified: 2026-06-20

## Must Learn

### CI/CD

- GitHub Actions workflow structure
- dependency caching
- matrix builds
- service containers
- artifacts
- status badges
- branch protection expectations

Projects:

- Add CI templates for Node, Python, Java, and Go learning repos.
- Add a reusable `README verification` checklist.

### Containers and orchestration

- Dockerfile basics
- Compose for local dependencies
- Kubernetes objects at concept level
- deployment, service, config, secret, ingress
- health/readiness checks

Projects:

- Add `examples/docker-compose-postgres`.
- Add `examples/kubernetes-basic-web-api`.

### Observability

- traces
- metrics
- logs
- context propagation
- OpenTelemetry Collector basics
- local observability stack

Projects:

- Instrument one backend app.
- Add `docs/observability-primer.md`.

### Security

- OWASP Top 10
- secrets handling
- dependency scanning
- least privilege
- secure defaults
- environment separation

Projects:

- Add `docs/security-checklist.md`.
- Add `.env.example` rules.

### Release and operations

- semantic versioning
- changelog
- rollback notes
- runbook
- incident review

Projects:

- Add `docs/release-checklist.md`.
- Add `docs/runbook-template.md`.

## Definition of Done

- Every learning repo has CI.
- Every external service uses `.env.example`.
- Every deployable app has health checks.
- At least one app exports traces/metrics/logs.

