# Privacy

This is a program you run yourself. It has no account with us, no analytics and no "phone home". The authors never see your API key, your profiles or your logs.

## What leaves your server

| What | Goes to | When |
|---|---|---|
| Your API key | NextDNS only (`api.nextdns.io`), in the `X-Api-Key` header over HTTPS | Every tool call that reads or changes something |
| Changes you ask for | NextDNS | When you ask |
| DNS test queries | NextDNS's DNS (`dns.nextdns.io/<profile>`), like a device using that profile | Only `check_domain` |
| What the tools return | Your AI app | When it calls a tool |

Nothing else: no telemetry, no crash reports. The only other request is the **update check**, if you turn it on (`UPDATE_CHECK`, off by default): once a day, a plain request to GitHub asking which release is newest, with no login and nothing about you. The Docker image, the extension and the code come from GitHub only when you install or update them.

## Encryption at a glance

| What | How |
|---|---|
| Connections to NextDNS | HTTPS, certificates checked |
| AI apps to the web version | HTTPS (your host or proxy provides it; `localhost` on your own computer) |
| The API key saved on the settings page | Fernet (AES with an HMAC check), key from `NEXTDNS_SECRET_KEY` or a random `secret.key` |
| The passphrase from `set-passphrase` | Only a hash: PBKDF2-SHA256, 600,000 rounds |
| AI apps' login keys, settings-page sessions | Only fingerprints (SHA-256): a copy of the files can't be used to log in |
| Files in the data folder | Owner-only (permissions 600) |

`LOGIN_PASSPHRASE` and `NEXTDNS_API_KEY` set as variables or in the settings file are plain text, like any hosting variable or settings file: keep the file `chmod 600` and your hosting account safe. Set `NEXTDNS_SECRET_KEY` on hosting, so a copy of the data folder alone is useless.

## What the server keeps

Everything is in the data folder: `~/.config/nextdns-agent-mcp/state` on a computer, `/data` in Docker and on hosting companies.

| File | What's in it | Personal? |
|---|---|---|
| `secrets.json` | The API key from the settings page, encrypted | The key, encrypted |
| `secret.key` | The encryption key, only when `NEXTDNS_SECRET_KEY` isn't set | Yes, keep it private |
| `settings.json` | Your choices on the settings page (modes, default profile, switches) | Profile IDs or names |
| `oauth.json` | Connected apps, their names, their profiles, key fingerprints | App names |
| `sessions.json` | Settings-page sign-ins you asked to remember, as fingerprints | No |
| `changes.json` | The last 300 changes: which tool, profile and app, when, and that part of the profile before and after | Your list entries and settings |
| `created.json` | IDs of profiles the AI made | No |
| `backups/` | Profile backups you made | Your full profile setup |

The change log and backups hold copies of profile settings and lists (denylist, allowlist, rewrites, blocklist choices). They never hold logs or analytics.

### About the fingerprints

A fingerprint is a one-way summary of a key: the server can check a key you show it, but nobody can turn the fingerprint back into the key.

## What the AI app sees

What the tools return: profile names and settings, list entries, analytics, and log entries when you ask for logs. Log entries include the domains your devices looked up, device names and client IP addresses (unless the profile drops them). What your AI provider does with conversations is up to them and your settings there.

The AI app never sees your API key or passphrase. Hide a profile ([profiles.md](profiles.md)) to keep it, and its logs, away from the AI completely.

## What NextDNS keeps

Logs and analytics are kept by NextDNS, per profile, as you set them: on or off, how long, which country, and whether to drop client IPs or domains (`profile_settings`, or the NextDNS dashboard). This server doesn't copy them.

`check_domain` makes a real query through the profile, so it appears in that profile's log, from the server's IP address.

## Logs of the server itself

The web version prints one line per web request (time, address, status) to its console, like most web servers, with no keys, passphrases or tool content. Hosting companies keep those console lines for a while. Tool calls aren't logged.

## The pages

The login and settings pages load nothing from other websites: no fonts, scripts, images or trackers. They can't be shown inside another site, and set no cookies except the sign-in cookie (and a light or dark choice, if you pick one).

## Deleting everything

1. Remove the server from your AI apps.
2. Delete the data folder (or the `/data` volume) and the settings file: `~/.config/nextdns-agent-mcp` on a computer.
3. Delete the API key at my.nextdns.io/account if you made one just for this.

Your NextDNS profiles, logs and analytics stay at NextDNS.
