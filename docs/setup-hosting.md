# Running it

First get your API key: sign in at [my.nextdns.io/account](https://my.nextdns.io/account), scroll to the bottom (API), show the key and copy it. More in the [official NextDNS API docs](https://nextdns.github.io/api/).

## Claude Desktop extension

Download `nextdns-agent-mcp.mcpb` from the latest release and open it. Claude Desktop asks for the API key, and whether Claude may change nothing (read only) or delete profiles and clear logs (always asked twice). It runs on your computer.

## On your computer, for any AI app

Needs [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/s17sh70x2jfl031ag/NextDNS-Agent-MCP.git
cd NextDNS-Agent-MCP
mkdir -p ~/.config/nextdns-agent-mcp && cp .env.example ~/.config/nextdns-agent-mcp/.env
```

Put the key in that file, then check it with `uv run nextdns-agent-mcp check` and add the server to your AI app with the command `uv run --directory /path/to/NextDNS-Agent-MCP nextdns-agent-mcp stdio` (the README shows Claude Desktop and Claude Code).

## The web version (phone, claude.ai)

It needs an HTTPS address. Once it runs:

1. Open `<address>/settings`, sign in with your passphrase, paste the API key, choose the profile modes.
2. In Claude: Settings, Connectors, Add custom connector, with `<address>/mcp`. The login page opens: tick the profiles, choose whether it may change them, type the passphrase.

Keep `/data` (or the config folder) on a disk that survives restarts: it holds the saved API key, logins, the change log and backups.

### Your own server (Docker)

Point a domain at the server. Next to `docker-compose.yml`, make a `.env` with:

```
NEXTDNS_DOMAIN=dns.example.com
LOGIN_PASSPHRASE=your passphrase
NEXTDNS_SECRET_KEY=some long random text
```

Then `docker compose up -d`. Caddy gets the HTTPS certificate by itself.

### Render

New, Blueprint, pick this repo: it reads `render.yaml`, runs the ready-made image and keeps a 1 GB disk. Fill in `LOGIN_PASSPHRASE`. The address Render gives is picked up by itself.

### Railway

New project from this repo: it builds the `Dockerfile` (`railway.json`). Then add a volume mounted at `/data`, set `LOGIN_PASSPHRASE` and `NEXTDNS_SECRET_KEY`, and generate a public domain. The address is picked up by itself.

### Your computer with a tunnel

`uv run nextdns-agent-mcp serve` listens on port 8766. Point a tunnel (for example Cloudflare Tunnel) at it and set `PUBLIC_URL` to the tunnel's HTTPS address.

## Updating

Each release has a tag (`vX.Y.Z`), a Docker image `ghcr.io/s17sh70x2jfl031ag/nextdns-agent-mcp` (tags: the version, major.minor and `latest`) and the `.mcpb` file. See [CHANGELOG.md](../CHANGELOG.md).
