# Updates

Each release has a version tag (`vX.Y.Z`), notes on the [releases page](https://github.com/s17sh70x2jfl031ag/NextDNS-Agent-MCP/releases), a Docker image and the Claude Desktop extension. What changed: [CHANGELOG.md](../CHANGELOG.md). Updates never touch your settings, change log or backups.

To hear about new releases: on GitHub, **Watch → Custom → Releases**.

| You run it | To update |
|---|---|
| Claude Desktop extension | Download the newest [`nextdns-agent-mcp.mcpb`](https://github.com/s17sh70x2jfl031ag/NextDNS-Agent-MCP/releases/latest/download/nextdns-agent-mcp.mcpb) and open it |
| On your computer (`uv tool`) | `uv tool upgrade nextdns-agent-mcp`, then restart your AI app (and `serve`, if you run it) |
| With `uvx` | Add `--refresh` once to the command, so it fetches the newest code |
| Docker Compose, ready-made image | `docker compose pull && docker compose up -d` |
| Docker Compose, built here | `git pull && docker compose up -d --build` |
| Render | **Manual Deploy** (it pulls `:latest` again) |
| Railway | **Redeploy** the service (it pulls `:latest` again) |

## Staying on one version

Use a version tag instead of `latest`: `ghcr.io/s17sh70x2jfl031ag/nextdns-agent-mcp:0.6.1` (exact) or `:0.6` (newest 0.6.x). With uv: `uv tool install git+https://github.com/s17sh70x2jfl031ag/NextDNS-Agent-MCP@v0.6.1`.

## Which version is running

`nextdns-agent-mcp version`, or the **About** tab on the settings page.
