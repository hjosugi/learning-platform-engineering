# NGINX Reverse Proxy Notes

Last verified: 2026-06-20

## Goal

Learn NGINX as a practical platform component:

- static file serving
- reverse proxy
- TLS termination
- HTTP load balancing
- WebSocket proxying
- HTTP/2 and HTTP/3 notes
- access logs and error logs
- rate limiting and request size limits

## Why This Stays Here

NGINX is infrastructure around applications, not an application by itself. It belongs in `learning-platform-engineering` alongside CI/CD, containers, Kubernetes, observability, and security.

## Planned Examples

```text
examples/
  nginx/
    static-site/
    reverse-proxy-node/
    websocket-proxy/
    tls-local/
    load-balancer/
```

## First Config To Build

Start with one local API and one reverse proxy:

```nginx
server {
    listen 8080;

    location /api/ {
        proxy_pass http://127.0.0.1:3000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Then add one concern at a time:

1. static files
2. logs
3. WebSocket upgrade headers
4. local TLS certificate
5. two upstream app instances
6. rate limits and body-size limits

## Things To Notice

- NGINX sees requests before the app does, so header forwarding matters.
- WebSocket proxying needs upgrade headers; ordinary HTTP proxying is not enough.
- TLS examples should use local/dev certificates and must not commit private keys.
- HTTP/3/QUIC support is useful to understand, but the first local lesson can stay on HTTP/1.1 or HTTP/2.
- Logs are part of the lesson; every example should explain where access and error logs go.

## Definition of Done

- Each config has a short explanation.
- Each example has a local run command.
- Logs are visible and explained.
- TLS examples use local/dev certificates only.
- WebSocket proxying is tested with a small local service.

## References

- NGINX documentation: https://nginx.org/en/docs/
- NGINX WebSocket proxying: https://nginx.org/en/docs/http/websocket.html
- NGINX HTTPS servers: https://nginx.org/en/docs/http/configuring_https_servers.html
- NGINX HTTP load balancer: https://nginx.org/en/docs/http/load_balancing.html
