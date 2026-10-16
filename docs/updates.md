# Updates

Each release has a version tag (`vX.Y.Z`), notes on the [releases page](https://github.com/s17sh70x2jfl031ag/NextDNS-Agent-MCP/releases), a Docker image and the Claude Desktop extension. What changed: [CHANGELOG.md](../CHANGELOG.md). Updates never touch your settings, change log or backups.

## Know when there's an update

- **On GitHub:** **Watch → Custom → Releases** on the repository. GitHub emails you each new release.
- **Your version:** `nextdns-agent-mcp version`, or the **About** tab on the settings page. Compare it with the [latest release](https://github.com/s17sh70x2jfl031ag/NextDNS-Agent-MCP/releases/latest).

The server itself never checks for updates: it doesn't contact anything but NextDNS.

## Update by hand

| You run it | To update |
|---|---|
| Claude Desktop extension | Download the newest [`nextdns-agent-mcp.mcpb`](https://github.com/s17sh70x2jfl031ag/NextDNS-Agent-MCP/releases/latest/download/nextdns-agent-mcp.mcpb) and open it |
| On your computer (`uv tool`) | `uv tool upgrade nextdns-agent-mcp`, then restart your AI app (and `serve`, if you run it) |
| With `uvx` | Add `--refresh` once to the command, so it fetches the newest code |
| Docker Compose, ready-made image | `docker compose pull && docker compose up -d` |
| Docker Compose, built here | `git pull && docker compose up -d --build` |
| `docker run` | `docker pull ghcr.io/s17sh70x2jfl031ag/nextdns-agent-mcp:latest`, then remove and start the container again (same volume) |
| Render | **Manual Deploy** (it pulls `:latest` again) |
| Railway | **Redeploy** the service (it pulls `:latest` again) |

## Update by itself (optional)

### On a hosting company

- **Railway:** in the service's **Settings → Source**, the image has **Configure auto updates**: Railway then redeploys when a new `latest` is published.
- **Render:** an image service doesn't redeploy by itself. Use a deploy hook from a scheduled job, or update by hand.
- Other hosts: look for "auto deploy" or "image updates" in their settings.

### On your own server (Docker)

[Watchtower](https://github.com/containrrr/watchtower) can pull new images and restart the container. Point it at this one container only, and keep a backup of the `/data` volume.

### On your computer

`uv tool upgrade --all` updates every tool you installed with uv. Run it now and then, or from a scheduled job (cron, launchd, Task Scheduler).

## Staying on one version

Use a version tag instead of `latest`: `ghcr.io/s17sh70x2jfl031ag/nextdns-agent-mcp:0.6.2` (exact) or `:0.6` (the newest 0.6.x). With uv: `uv tool install --force git+https://github.com/s17sh70x2jfl031ag/NextDNS-Agent-MCP@v0.6.2`.

## Going back

Something wrong after an update? Go back to the version before:

- Docker, Render, Railway: change the image tag to the previous version (for example `:0.6.1`) and redeploy.
- `uv tool`: `uv tool install --force git+https://github.com/s17sh70x2jfl031ag/NextDNS-Agent-MCP@v0.6.1`.
- Extension: open the previous release's `.mcpb` from the [releases page](https://github.com/s17sh70x2jfl031ag/NextDNS-Agent-MCP/releases).

Your data folder works with the version before too. Then tell us what went wrong in an [issue](https://github.com/s17sh70x2jfl031ag/NextDNS-Agent-MCP/issues/new?template=bug_report.yml).
