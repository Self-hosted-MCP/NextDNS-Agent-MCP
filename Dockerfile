# nextdns-agent-mcp as a web server (serve mode). Works on amd64 and arm64.
FROM python:3.14-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.11.19 /uv /bin/uv

WORKDIR /app

# dependencies first, so code changes rebuild fast
COPY pyproject.toml uv.lock README.md LICENSE NOTICE ./
RUN uv sync --frozen --no-install-project --no-dev

COPY src ./src
RUN uv sync --frozen --no-dev

# Everything that must survive a restart (the API key saved on the settings page, logins, the change log,
# backups) lives in /data. Mount a persistent volume or disk there. Without one it still works, but after each
# restart you log in again, the change log starts empty and the backups are gone.
ENV HOST=0.0.0.0 \
    PORT=8766 \
    NEXTDNS_CONFIG_DIR=/data \
    NEXTDNS_DATA_DIR=/data \
    PATH="/app/.venv/bin:$PATH"
EXPOSE 8766

HEALTHCHECK --interval=60s --timeout=5s CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ.get(\"PORT\", \"8766\")}/health')"

CMD ["nextdns-agent-mcp", "serve"]
