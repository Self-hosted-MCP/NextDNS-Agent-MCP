# Claude Desktop extension

The quickest way on Claude Desktop: one file, no terminal and no settings file. Claude Desktop runs it on your computer, for Claude Desktop only. For other apps, or your phone, see [setup-computer.md](setup-computer.md) and [setup-hosting.md](setup-hosting.md).

## What you need

- [Claude Desktop](https://claude.ai/download) on Mac, Windows or Linux, recent enough to install extensions (**Settings → Extensions**).
- Your NextDNS API key: sign in at [my.nextdns.io/account](https://my.nextdns.io/account), scroll to the bottom (**API**), show the key and copy it.

## Install

1. Download [`nextdns-agent-mcp.mcpb`](https://github.com/s17sh70x2jfl031ag/NextDNS-Agent-MCP/releases/latest/download/nextdns-agent-mcp.mcpb) from the latest release.
2. Open it (double-click), or in Claude Desktop go to **Settings → Extensions** and drag it in.
3. Claude Desktop shows what it is and asks for:

   | Field | What to put |
   |---|---|
   | **NextDNS API key** (required) | The key you copied |
   | **Read only** | On: Claude can look at everything but change nothing. Off by default |
   | **Allow deleting profiles and clearing logs** | Claude always asks you twice first. Off: it can never do these. On by default |

4. Click **Install**, and make sure the extension is turned on.
5. Start a new chat and ask: *"Use the NextDNS tools: what got blocked today?"*

The first start takes a little longer: Claude Desktop sets up the program and its packages once.

## What you get

All 23 tools ([tools.md](tools.md)), the change log and undo, and backups. Changes show in the change log as made by "Claude Desktop". Ask *"what did you change today?"* or *"undo that"*.

## Choose what Claude may do with each profile

The extension has no settings page (that's the [web version](setup-computer.md#the-web-version-on-your-computer-optional)). To hide a profile or make it read only, add a line to `~/.config/nextdns-agent-mcp/.env` (make the folder and file if they don't exist):

```
NEXTDNS_PROFILES=abc123=full,Kids=read,Work laptop=hidden
```

The extension reads that file too. Restart Claude Desktop after changing it. More in [profiles.md](profiles.md).

## Change the key or the switches

**Settings → Extensions → NextDNS Agent → Configure**: change the API key or the two switches, then restart the extension.

## Where your key is kept

Claude Desktop keeps the key (the extension marks it as sensitive, so it isn't shown) and passes it to the program when it starts. The key goes only to NextDNS; Claude never sees it. The change log and backups are in `~/.config/nextdns-agent-mcp/state`, like the other ways of running it on a computer.

## Update

Download the newest `.mcpb` and open it again. Your change log and backups stay. See [updates.md](updates.md).

## Remove

**Settings → Extensions**, then remove **NextDNS Agent**. To remove everything, also delete `~/.config/nextdns-agent-mcp`.

## If it doesn't work

- **The tools don't appear:** check the extension is turned on, then start a new chat. Restart Claude Desktop if needed.
- **"NextDNS refused the API key":** copy the key again and set it under **Configure**.
- **Nothing happens, or an error about uv or Python:** Claude Desktop sets these up itself; make sure it's up to date, and that your computer can reach the internet for the first start.
- More in [troubleshooting.md](troubleshooting.md).

## How it's built

The `.mcpb` file is a zip of this project plus [`extension/manifest.json`](../extension/manifest.json). Claude Desktop runs it with uv, from the exact package versions in `uv.lock`, with the command `nextdns-agent-mcp stdio`. Each release builds it, checks it with Anthropic's own validator, and attaches it to the release ([the workflow](../.github/workflows/extension.yml)). To build it yourself: `python3 scripts/build_mcpb.py`.
