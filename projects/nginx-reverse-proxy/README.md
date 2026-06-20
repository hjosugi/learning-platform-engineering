# NGINX Reverse Proxy

Hands-on NGINX config for static files, health checks, and reverse proxying to a local backend.

## Inspect Without NGINX

```bash
python3 projects/nginx-reverse-proxy/check_config.py
```

## Run When NGINX Is Installed

```bash
nginx -t -c "$PWD/projects/nginx-reverse-proxy/nginx.conf" -p "$PWD/projects/nginx-reverse-proxy"
```

## What To Learn

- `server` and `location` blocks
- `proxy_pass`
- health endpoint behavior
- headers that preserve request context

