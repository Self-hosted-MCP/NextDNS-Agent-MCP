# Setup on a hosting company

Always on, so your phone and the Claude or ChatGPT website can use it any time. No terminal needed. About 10 minutes, a few dollars a month.

Every option runs the ready-made image `ghcr.io/s17sh70x2jfl031ag/nextdns-agent-mcp` (or builds this repo's `Dockerfile`) and needs three things:

1. **A passphrase**, `LOGIN_PASSPHRASE`, 6 characters or more. It locks the settings page and the login AI apps use.
2. **A secret key**, `NEXTDNS_SECRET_KEY`: any long random text. It encrypts the API key you paste on the settings page. Never change it later (or paste the API key again if you do).
3. **A disk at `/data`** that survives restarts. It keeps the saved API key, logins, the change log and backups. Without one it still works, but after each restart you paste the key and log in again, and undo history and backups are gone.

The server picks up its public address by itself on Render and Railway. Elsewhere, set `PUBLIC_URL` to it.

## One click: Render

<a href="https://render.com/deploy?repo=https://github.com/s17sh70x2jfl031ag/NextDNS-Agent-MCP"><img src="https://render.com/images/deploy-to-render-button.svg" alt="Deploy to Render"></a>

1. Press the button (or in Render: **New → Blueprint**, and pick this repository). It reads [`render.yaml`](../render.yaml).
2. Fill in `LOGIN_PASSPHRASE`. Render makes `NEXTDNS_SECRET_KEY` for you and adds a 1 GB disk at `/data`.
3. Render uses its smallest paid instance, because the free one can't keep a disk and falls asleep.
4. When it's live, open `https://<your-app>.onrender.com/settings`, sign in, and paste your API key.

## Railway

1. In Railway: **New project → Docker image**: `ghcr.io/s17sh70x2jfl031ag/nextdns-agent-mcp:latest`. (Or **Deploy from GitHub repo** with this repository: it builds the `Dockerfile`, see [`railway.json`](../railway.json).)
2. **Variables:** `LOGIN_PASSPHRASE`, `NEXTDNS_SECRET_KEY` (Railway can make one: `${{secret(64)}}`) and `PORT=8766`.
3. **Volume:** add one, mounted at `/data`.
4. **Settings → Networking:** generate a public domain on port 8766. **Healthcheck path:** `/health`.
5. Open `https://<your-app>.up.railway.app/settings`, sign in, and paste your API key.

## Any other hosting company

Anything that runs a Docker image works (Fly.io, Koyeb, Northflank, Coolify, a NAS, ...):

| What | Value |
|---|---|
| Image | `ghcr.io/s17sh70x2jfl031ag/nextdns-agent-mcp:latest` (or a version, like `:0.6`) |
| Port | 8766 (HTTP) |
| Health check | `/health` |
| Disk | at `/data` |
| Variables | `LOGIN_PASSPHRASE`, `NEXTDNS_SECRET_KEY`, `PUBLIC_URL=https://your-address` |

The image works on amd64 and arm64.

## Then

1. Open `https://your-address/settings`, sign in with your passphrase.
2. **API key** tab: paste it, press **Test and save**.
3. **Profiles** tab: choose what the AI may do with each one.
4. Connect your AI apps to `https://your-address/mcp`: [connect-your-ai.md](connect-your-ai.md).

## Putting the API key in the variables instead

You can set `NEXTDNS_API_KEY` as a variable instead of pasting it on the settings page. It then shows on the page as "comes from the settings file or hosting variables" and can only be changed there. The same goes for every other setting ([settings.md](settings.md)).

## Updates

`latest` follows the newest release. Redeploy (or restart) to get it. To stay on one version, use a version tag like `:0.6.1`. See [updates.md](updates.md).
