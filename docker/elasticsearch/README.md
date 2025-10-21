# Elasticsearch (dev) — Docker Compose

This folder contains a small Docker Compose setup to run a single-node Elasticsearch instance for local development.

Files

- `docker-compose.yaml` — Compose file that starts Elasticsearch 8.19.5 in single-node mode.
- `config/overrides.yml` — Additional Elasticsearch YAML settings (CORS) mounted into the container.

Quick start (PowerShell)

```powershell
# Validate compose file
docker compose -f .\docker-compose.yaml config

# Start in background
docker compose -f .\docker-compose.yaml up -d

# Follow logs
docker compose -f .\docker-compose.yaml logs -f elasticsearch

# Check container health
docker inspect -f '{{json .State.Health}}' elasticsearch

# Query HTTP API
curl http://127.0.0.0.1:9200/
```

What this dev setup does

- Binds Elasticsearch HTTP to localhost:9200 only (`127.0.0.1:9200:9200`) to avoid exposing the service to your LAN.
- Uses a named Docker volume `elasticsearch-data` to persist data across restarts.
- Disables Elasticsearch security (`xpack.security.enabled: false`) for convenience in local development. IMPORTANT: do NOT use this in production.
- Mounts `config/overrides.yml` (read-only) into `/usr/share/elasticsearch/config/overrides.yml` to provide YAML-friendly settings (for example CORS) that are otherwise error-prone when passed via environment variables.
- Adds a simple healthcheck so Docker Compose can report readiness.

CORS and overrides

- `config/overrides.yml` contains:

```yaml
http.cors.allow-origin: "*"
http.cors.enabled: true
```

This is a development convenience only. Replace `"*"` with a specific origin and remove the development CORS policy for any public deployment.

Memory and JVM heap

- The compose file sets `ES_JAVA_OPTS` to `-Xms512m -Xmx512m`. Increase this for heavier local workloads, but keep the heap at or below ~50% of your host RAM.

Switching to secure/production mode

- Remove `xpack.security.enabled: "false"` from the environment and follow Elasticsearch docs to configure TLS and built-in users.
- Consider using a production Compose override (e.g., `docker-compose.prod.yml`) that sets volumes, memory limits, and networking appropriately.

If you want, I can:

- Add a `docker-compose.prod.yml` that keeps security enabled and shows how to mount keystore/certs.
- Add a small script to wait for readiness and run a quick health check.
