# Troubleshooting

Start with `nextdns-agent-mcp check`: it tests the key and lists your profiles with their modes, without changing anything. On the web version, the settings page shows the same.

## The key and profiles

**"NextDNS refused the API key".** Copy the key again from the bottom of [my.nextdns.io/account](https://my.nextdns.io/account) (no spaces around it). If you made a new key, the old one stops working.

**"No NextDNS API key".** The server didn't find one: not in the settings file (`~/.config/nextdns-agent-mcp/.env`), not in the environment, not saved on the settings page. Check the file name starts with a dot, and that the line is `NEXTDNS_API_KEY=...`.

**The AI says a profile doesn't exist.** It may be hidden (profile modes), or not ticked for that app when it connected. Check the **Profiles** and **Apps** tabs on the settings page, or `check`.

**"read only for this app".** The profile is in read mode, the app wasn't allowed to change things when it logged in, or read-only mode is on.

**"Which profile?"** You have several profiles and no default. Name one, or set a default ([profiles.md](profiles.md#the-default-profile)).

**"Too many changes in the last minute".** The brake (`NEXTDNS_CHANGE_LIMIT`, 30 by default). Wait a minute.

## Changes and logs

**A change doesn't show yet.** NextDNS needs a few seconds before its DNS servers use it, and devices cache answers for a while. `check_domain` makes a fresh query.

**No logs, or `watch_logs` shows nothing.** Logs may be off for the profile: ask for its settings. By default only useful queries show; ask for raw logs to see every query.

**Undo says the profile "changed again since".** Something changed it after (the NextDNS dashboard, another app, a later change). Undo anyway drops those later changes too: use `force`, or the box on the settings page.

**The saved API key can't be read after a move.** `NEXTDNS_SECRET_KEY` changed, or `secret.key` was lost. Paste the key again on the settings page.

## The AI app

**The app doesn't show the tools.** Restart the app after adding the server. On a computer, use the full path of the command ([connect-your-ai.md](connect-your-ai.md#before-you-start-the-command-path)). Try the command yourself: `nextdns-agent-mcp stdio` should wait silently (Ctrl+C to stop).

**"Redirect not allowed" on login.** The app's return address isn't on the list. Add its domain to `ALLOWED_REDIRECT_HOSTS` ([settings.md](settings.md)).

**The login page says the link expired.** Links last 10 minutes. Start connecting again in the AI app.

**The login page shows no profiles.** The server has no working API key yet: open the settings page and paste it. Or every profile is hidden.

**The app was connected, now it isn't.** Its key renews for 90 days; after that, or after **Disconnect**, connect again.

## The web version

**Locked out of the settings page.** Five wrong tries lock it for 15 minutes.

**Forgot the passphrase.** Set a new one (`set-passphrase`, or change `LOGIN_PASSPHRASE`) and restart.

**`serve` says "Set a passphrase first".** `LOGIN_PASSPHRASE` (6+ characters) or `LOGIN_HASH` must be set.

**Phones can't connect.** The server needs a public HTTPS address, set as `PUBLIC_URL` (Render and Railway set it by themselves). `localhost` only works on the same computer.

**"Invalid Host header" from a proxy.** Pass the original `Host` header through, and set `PUBLIC_URL` to the public address.

**Settings, logins or backups vanish after a restart.** The data folder isn't on a disk that survives restarts: add a volume at `/data` ([setup-hosting.md](setup-hosting.md)).

Still stuck? Open an [issue](https://github.com/s17sh70x2jfl031ag/NextDNS-Agent-MCP/issues/new?template=bug_report.yml) with what you asked, what happened, and `nextdns-agent-mcp version`. Leave out your API key and profile IDs.
