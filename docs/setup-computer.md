# Setup on your computer

Free, about 5 minutes, on Mac, Windows or Linux. Any AI app on the same computer can use it. Using Claude Desktop only? The [extension](claude-desktop-extension.md) is even quicker.

## 1. Install uv

[uv](https://docs.astral.sh/uv/getting-started/installation/) is a small free tool that installs Python programs (it brings Python itself if you don't have it).

- Mac and Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## 2. Install the server

```bash
uv tool install git+https://github.com/Self-hosted-MCP/NextDNS-Agent-MCP
```

This gives you the `nextdns-agent-mcp` command. Check it with `nextdns-agent-mcp version`.

## 3. Add your API key

1. Sign in at [my.nextdns.io/account](https://my.nextdns.io/account).
2. Scroll to the bottom, to **API**. Show the key and copy it.
3. Make the settings file and put the key in it:

```bash
mkdir -p ~/.config/nextdns-agent-mcp
```

```bash
echo "NEXTDNS_API_KEY=paste-your-key-here" > ~/.config/nextdns-agent-mcp/.env
```

```bash
chmod 600 ~/.config/nextdns-agent-mcp/.env
```

On Windows the folder is `C:\Users\you\.config\nextdns-agent-mcp\`. Make it, and a file named `.env` in it with the line `NEXTDNS_API_KEY=...`.

The [`.env.example`](../.env.example) file lists every other setting you can add there, all optional. See [settings.md](settings.md).

## 4. Choose what the AI may do (optional)

By default the AI may read and change every profile. To keep one away from it, or make one read only, add a line like this to the settings file (the profile IDs are in `nextdns-agent-mcp check`):

```
NEXTDNS_PROFILES=abc123=full,def456=read,ghi789=hidden
```

More in [profiles.md](profiles.md).

## 5. Check it

```bash
nextdns-agent-mcp check
```

It tests the key and lists each profile with what the AI may do. It changes nothing.

## 6. Connect your AI app

For example Claude Code:

```bash
claude mcp add nextdns -s user -- nextdns-agent-mcp stdio
```

Every other app, step by step: [connect-your-ai.md](connect-your-ai.md).

## The web version on your computer (optional)

The web version adds the settings page (API key, profile modes, connected apps, the change log with Undo buttons, backups) and lets apps connect over the internet.

1. Choose a passphrase (6 characters or more). Only its hash is saved:

   ```bash
   nextdns-agent-mcp set-passphrase
   ```

2. Start it:

   ```bash
   nextdns-agent-mcp serve
   ```

3. Open [http://localhost:8766/settings](http://localhost:8766/settings) and sign in.

It runs while that terminal is open. Apps on the same computer can also connect to `http://localhost:8766/mcp`.

### On your phone, through a tunnel

Your phone can't reach `localhost`. A tunnel gives your computer a public HTTPS address, for free:

- **Cloudflare Tunnel:** `cloudflared tunnel --url http://localhost:8766` prints an address like `https://something.trycloudflare.com`.
- **Tailscale Funnel:** `tailscale funnel 8766`.

Put that address in the settings file as `PUBLIC_URL=https://...`, restart `serve`, and connect your phone's AI app to `https://.../mcp` ([connect-your-ai.md](connect-your-ai.md)). It works only while your computer is on: for always on, use [a hosting company](setup-hosting.md).

## Where things are

| What | Where |
|---|---|
| Settings file | `~/.config/nextdns-agent-mcp/.env` |
| Data folder (change log, logins, backups) | `~/.config/nextdns-agent-mcp/state` |
| The command | `~/.local/bin/nextdns-agent-mcp` (`which nextdns-agent-mcp`) |

## Remove it

```bash
uv tool uninstall nextdns-agent-mcp
```

Then delete `~/.config/nextdns-agent-mcp` if you don't want your settings and change log any more, and remove it from your AI apps. Your NextDNS account is not touched.
