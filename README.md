# NextDNS-Agent-MCP

Use your NextDNS account from Claude, ChatGPT, Codex and other AI apps. Ask in plain words: "what got blocked on my phone today?", "add OISD to my blocklists", "unblock example.com".

> Not made by or affiliated with NextDNS. It uses the public [NextDNS API](https://nextdns.github.io/api/) with your own API key.

**Status: 0.6, early.** Runs on your computer for one AI app, or as a small web server with a login and a settings page, so Claude on your phone and claude.ai can use it too.

## What it can do

| Tool | What it does |
|---|---|
| `profiles` | The profiles this app may use, and whether it may change them |
| `profile` | One profile's settings: security, privacy, parental control, lists, rewrites, settings, setup addresses |
| `catalog` | What you can pick from: blocklists, native trackers, services, categories, TLDs |
| `analytics` | Counts: allowed/blocked, top domains, block reasons, devices, IPs, protocols, and more, also over time |
| `logs` | Search the query log, or get a download link |
| `list_entries` | Add, remove, turn on or off domains in the denylist or allowlist |
| `privacy` | Add or remove blocklists and native tracker protection, disguised trackers, affiliate links |
| `security` | Turn protections on or off, block or unblock TLDs |
| `parental_control` | Block services and categories, pause them, recreation time, safe search, YouTube mode |
| `rewrites` | Add or remove DNS rewrites (point a name to your own IP) |
| `profile_settings` | Rename, logs (on/off, how long, where), block page, ECS, cache boost, CNAME flattening, Web3 |
| `create_profile` | A new profile: copy of another, recommended start, or empty |
| `delete_profile` | Delete a profile (off unless you allow it) |
| `clear_logs` | Delete a profile's logs (off unless you allow it) |
| `changes` | What was changed through this app |
| `undo` | Put a profile back the way it was before one change |
| `check_domain` | Is a domain blocked, and why (a real test query, the lists and the log) |
| `watch_logs` | Watch queries live for a few seconds, for example while you open an app |
| `chart` | A picture of any analytics report, over time or as bars |
| `compare_profiles` | What differs between two profiles |
| `backup` / `backups` | Save a full copy of a profile, and list the copies |
| `restore_backup` | Put a copy back (asks twice first), or make a new profile from it |

## Safety

- The AI may do everything the NextDNS API allows, on the profiles you let it use.
- **Deleting a profile, clearing logs or overwriting a profile from a backup needs a double confirmation:** the first call does nothing and returns a code; the AI has to ask you, and only after you say yes can it call again with that code. You can also turn deletes off completely.
- Every change is saved with how things were before, so `undo` (or the Undo button on the settings page) can put it back. If the profile changed again since, undo stops and asks first.
- Each profile is **full** (read and change, the default), **read** (read only) or **hidden**.
- On the web version, each AI app gets only the profiles you tick when it connects, and you choose whether it may change them. You can change that or disconnect it on the settings page.
- `NEXTDNS_READ_ONLY=on` blocks every change. At most 30 changes a minute (`NEXTDNS_CHANGE_LIMIT`).
- Your API key stays on your computer or server (encrypted when saved on the settings page) and goes only to NextDNS.

## Ways to run it

You need your NextDNS API key: sign in at https://my.nextdns.io/account, scroll to the bottom (API), show the key and copy it. More in the [official NextDNS API docs](https://nextdns.github.io/api/).

| Way | For | How |
|---|---|---|
| Claude Desktop extension | the easiest, one computer | Download `nextdns-agent-mcp.mcpb` from the latest release, open it, paste the API key |
| Your computer (stdio) | Claude Desktop, Claude Code, Codex | See below |
| Web version | your phone and claude.ai | Your own server (Docker), Render or Railway. See below |

### Your computer

1. Copy `.env.example` to `~/.config/nextdns-agent-mcp/.env` and fill in the key (or leave it out and use the web version's settings page).
2. Check it: `uv run nextdns-agent-mcp check`
3. Add it to your AI app, for example Claude Desktop (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "nextdns": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/NextDNS-Agent-MCP", "nextdns-agent-mcp", "stdio"]
    }
  }
}
```

Or in Claude Code: `claude mcp add nextdns -- uv run --directory /path/to/NextDNS-Agent-MCP nextdns-agent-mcp stdio`

### Web version

It needs an HTTPS address so your phone and claude.ai can reach it. Pick one:

- **Your own server with Docker:** point a domain at the server, make a `.env` with `NEXTDNS_DOMAIN`, `LOGIN_PASSPHRASE` (6+ characters) and `NEXTDNS_SECRET_KEY` (long random text, never change it), then `docker compose up -d`. Caddy gets the certificate.
- **Render:** New, Blueprint, this repo (`render.yaml`). Fill in `LOGIN_PASSPHRASE`. It uses the ready-made image and keeps a 1 GB disk for your data.
- **Railway:** new project from this repo (it builds the `Dockerfile`). Add a volume at `/data`, set `LOGIN_PASSPHRASE` and `NEXTDNS_SECRET_KEY`, and give it a public domain. The address is picked up by itself.
- **Your computer with a tunnel:** `uv run nextdns-agent-mcp serve` and a tunnel (for example Cloudflare Tunnel) to port 8766; set `PUBLIC_URL` to the tunnel's address.

Then:

1. Open `<your address>/settings`, sign in with the passphrase, paste the API key, choose the profile modes.
2. In Claude: Settings, Connectors, Add custom connector, with `<your address>/mcp`. A login page opens: tick the profiles, type the passphrase.

Every release builds the image `ghcr.io/s17sh70x2jfl031ag/nextdns-agent-mcp` (tags: version, major.minor, latest) and the `.mcpb` extension.

## More

- [Tools](docs/tools.md): every tool and what it takes
- [Safety](docs/safety.md): modes, double confirmation, undo, your data
- [Settings](docs/settings.md): every setting
- [Running it](docs/setup-hosting.md): extension, computer, Docker, Render, Railway, tunnel
- [Troubleshooting](docs/troubleshooting.md)

## License

MIT. See [LICENSE](LICENSE).
