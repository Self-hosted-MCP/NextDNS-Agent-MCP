# Privacy

This is a program you run yourself. It has no account with us, no analytics and no "phone home". The authors never see your API key, your profiles or your logs.

## Where your data goes

| Data | Goes to |
|---|---|
| Your API key | NextDNS only (`api.nextdns.io`), in the `X-Api-Key` header over HTTPS |
| Your profiles, lists, logs, analytics | Read from NextDNS, then passed to your AI app when it asks |
| DNS test queries (`check_domain`) | `dns.nextdns.io/<profile>`, like a device using that profile |

**Your AI app sees what the tools return.** Log entries include domains, device names and client IP addresses. What your AI provider does with conversations is up to them and your settings there. Use profile modes ([profiles.md](profiles.md)) to keep a profile away from the AI altogether.

## What's kept, and where

Everything is in the data folder: `~/.config/nextdns-agent-mcp/state` on a computer, `/data` in Docker and on hosting companies. See [how-it-works.md](how-it-works.md#whats-stored) for each file.

- **The API key** typed on the settings page is encrypted (Fernet, AES with an HMAC check). The encryption key is `NEXTDNS_SECRET_KEY` if you set one, otherwise a random `secret.key` next to the data. Set the variable on hosting, so a copy of the data folder alone is useless.
- **The passphrase** is never stored in plain text by `set-passphrase` (PBKDF2-SHA256, 600,000 rounds). `LOGIN_PASSPHRASE` as a variable is plain, like any hosting variable.
- **Login keys and sessions** are stored only as fingerprints (SHA-256).
- **The change log and backups** hold copies of profile settings and lists (domains in your denylist and allowlist, rewrites). They hold no logs.
- Files are written owner-only (permissions 600).

## What NextDNS keeps

Logs and analytics are kept by NextDNS, per profile, as you set them (`profile_settings`: on or off, how long, which country, whether to drop client IPs or domains). This server doesn't copy them.

`check_domain` makes a real query through the profile, so it appears in that profile's log, from the server's IP address.

## The pages

The login and settings pages load nothing from other websites: no fonts, scripts, images or trackers. They can't be shown inside another site, and set no cookies except the sign-in cookie (and a light or dark choice, if you pick one).

## Removing everything

Delete the data folder (or the `/data` volume), and the API key from NextDNS if you made one just for this (my.nextdns.io/account). Disconnect the server in your AI apps.
