# Updates

Each release has a version tag (`vX.Y.Z`), notes on the [releases page](https://github.com/s17sh70x2jfl031ag/NextDNS-Agent-MCP/releases), a Docker image and the Claude Desktop extension. What changed: [CHANGELOG.md](../CHANGELOG.md). Updates never touch your settings, change log or backups.

## Know when there's an update

- **On GitHub:** **Watch → Custom → Releases** on the repository. GitHub emails you each new release.
- **Your version:** `nextdns-agent-mcp version`, or the **About** tab on the settings page. Compare it with the [latest release](https://github.com/s17sh70x2jfl031ag/NextDNS-Agent-MCP/releases/latest).

- **Let the server tell you:** turn on the update check, on the settings page (**About** tab) or with `UPDATE_CHECK=on`. Once a day it asks GitHub which release is newest (a plain request, nothing about you). When there's a new one, the About tab says so, and so does your AI app the next time it lists your profiles. Off by default.

## Update by hand

| You run it | To update |
|---|---|
| Claude Desktop extension | Download the newest [`nextdns-agent-mcp.mcpb`](https://github.com/s17sh70x2jfl031ag/NextDNS-Agent-MCP/releases/latest/download/nextdns-agent-mcp.mcpb) and open it |
| On your computer (`uv tool`) | `nextdns-agent-mcp update` (installs the newest release, or says you're up to date), then restart your AI app (and `serve`, if you run it) |
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

### On your own server (Docker Compose)

[`scripts/update.sh`](../scripts/update.sh) moves your copy to the newest official release and restarts it, only if there's a new one. Run it by hand, or every week with cron (`crontab -e`):

```
0 4 * * 1 cd /path/to/NextDNS-Agent-MCP && ./scripts/update.sh >> update.log 2>&1
```

It refuses to run if you changed tracked files in your copy. With the ready-made image instead of `build: .`, `docker compose pull && docker compose up -d` does the same, and [Watchtower](https://github.com/containrrr/watchtower) can do it for you.

### Your own fork on a hosting company

If your hosting company builds from your fork of this repository, the fork can follow official releases by itself: in your fork, turn on Actions, then add the repository variable `AUTO_UPDATE` = `on` (**Settings → Secrets and variables → Actions → Variables**). Every Monday, [the workflow](../.github/workflows/update-from-releases.yml) merges the newest release into your fork, and your host rebuilds. It never runs in the original repository, and it stops (without changing anything) if the release conflicts with your own changes.

### On your computer

`nextdns-agent-mcp update` installs the newest release with uv and does nothing if you're up to date. To run it every week:

<details>
<summary><b>Mac</b></summary>

Save as `~/Library/LaunchAgents/com.nextdns-agent-mcp.update.plist` (replace `YOU` with your user name):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.nextdns-agent-mcp.update</string>
  <key>ProgramArguments</key>
  <array><string>/Users/YOU/.local/bin/nextdns-agent-mcp</string><string>update</string></array>
  <key>StartCalendarInterval</key><dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>9</integer></dict>
  <key>StandardOutPath</key><string>/tmp/nextdns-agent-mcp-update.log</string>
</dict>
</plist>
```

Turn it on with `launchctl bootstrap gui/$(id -u)` and that path.

</details>

<details>
<summary><b>Linux</b></summary>

`crontab -e`, then add:

```
0 9 * * 1 $HOME/.local/bin/nextdns-agent-mcp update >> $HOME/.cache/nextdns-agent-mcp-update.log 2>&1
```

</details>

<details>
<summary><b>Windows</b></summary>

In Task Scheduler, create a weekly task that runs `nextdns-agent-mcp` with the argument `update`.

</details>

Restart your AI app after an update (and `serve`, if you run it).

### Claude Desktop extension

Download the newest `.mcpb` and open it again. The update check tells you when there's one.

## Staying on one version

Use a version tag instead of `latest`: `ghcr.io/s17sh70x2jfl031ag/nextdns-agent-mcp:0.6.2` (exact) or `:0.6` (the newest 0.6.x). With uv: `uv tool install --force git+https://github.com/s17sh70x2jfl031ag/NextDNS-Agent-MCP@v0.6.2`.

## Going back

Something wrong after an update? Go back to the version before:

- Docker, Render, Railway: change the image tag to the previous version (for example `:0.6.1`) and redeploy.
- `uv tool`: `uv tool install --force git+https://github.com/s17sh70x2jfl031ag/NextDNS-Agent-MCP@v0.6.1`.
- Extension: open the previous release's `.mcpb` from the [releases page](https://github.com/s17sh70x2jfl031ag/NextDNS-Agent-MCP/releases).

Your data folder works with the version before too. Then tell us what went wrong in an [issue](https://github.com/s17sh70x2jfl031ag/NextDNS-Agent-MCP/issues/new?template=bug_report.yml).
