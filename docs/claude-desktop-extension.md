# Claude Desktop extension

The quickest way on Claude Desktop: one file, no terminal and no settings file. Claude Desktop runs it on your computer.

## Install

1. Download [`nextdns-agent-mcp.mcpb`](https://github.com/s17sh70x2jfl031ag/NextDNS-Agent-MCP/releases/latest/download/nextdns-agent-mcp.mcpb) from the latest release.
2. Open it (double-click), or in Claude Desktop go to **Settings → Extensions** and drag it in.
3. Claude Desktop asks for:
   - **NextDNS API key** (required): sign in at [my.nextdns.io/account](https://my.nextdns.io/account), scroll to the bottom (**API**), show the key and copy it.
   - **Read only**: on, Claude can look at everything but change nothing. Off by default.
   - **Allow deleting profiles and clearing logs**: Claude always asks you twice first. Off, it can never do these. On by default.
4. Start a new chat and ask: *"Use the NextDNS tools: what got blocked today?"*

The key is kept by Claude Desktop (it marks it as sensitive) and goes only to NextDNS.

## What you get

All 23 tools, the change log and undo, and backups. Changes show in the change log as made by "Claude Desktop".

The extension has no settings page (that's the [web version](setup-computer.md#the-web-version-on-your-computer-optional)). To hide a profile or make it read only, add `NEXTDNS_PROFILES` to `~/.config/nextdns-agent-mcp/.env` ([profiles.md](profiles.md)): the extension reads that file too.

## Update

Download the newest `.mcpb` and open it again. Your change log and backups stay (they're in `~/.config/nextdns-agent-mcp/state`).

## Remove

**Settings → Extensions**, then remove **NextDNS Agent**.

## How it's built

The `.mcpb` file is a zip of this project plus [`extension/manifest.json`](../extension/manifest.json). Claude Desktop runs it with uv, from the exact package versions in `uv.lock`. Each release builds it, checks it with Anthropic's own validator, and attaches it to the release ([the workflow](../.github/workflows/extension.yml)). To build it yourself: `python3 scripts/build_mcpb.py`.
