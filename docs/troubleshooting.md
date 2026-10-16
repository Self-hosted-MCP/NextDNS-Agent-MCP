# Troubleshooting

> [!TIP]
> Start here: `nextdns-agent-mcp check` tests the API key and lists every profile with what the AI may do with it. It changes nothing. On the web version, the settings page shows the same. On a hosting company, look at the service's logs.

## The API key

<details>
<summary>"NextDNS refused the API key"</summary>

- Copy the key again from the bottom of [my.nextdns.io/account](https://my.nextdns.io/account), with no spaces before or after it.
- If you made a new key, the old one stopped working: update it everywhere you use it.
- In a settings file, the line is `NEXTDNS_API_KEY=yourkey`, with no quotes and no spaces around `=`.

</details>

<details>
<summary>"No NextDNS API key"</summary>

The server didn't find one: not in the settings file, not in the environment, not saved on the settings page.

- The settings file is `~/.config/nextdns-agent-mcp/.env`. The name starts with a dot; some editors add `.txt` at the end, so check.
- `nextdns-agent-mcp check` prints which file it reads.
- In an AI app's `env` block, the name is `NEXTDNS_API_KEY`.

</details>

<details>
<summary>The saved API key can't be read after a move</summary>

`NEXTDNS_SECRET_KEY` changed, or the `secret.key` file was lost, so the key saved on the settings page can't be decrypted. Paste the API key again on the settings page. On hosting, keep `NEXTDNS_SECRET_KEY` the same forever.

</details>

<details>
<summary>"Can't reach NextDNS right now"</summary>

The server couldn't connect to `api.nextdns.io`. Check the internet connection of the computer or server, and any firewall or proxy. It already tried a few times before saying so.

</details>

## Profiles

<details>
<summary>The AI says a profile doesn't exist</summary>

- It may be **hidden** (profile modes): the **Profiles** tab, or `NEXTDNS_PROFILES`.
- On the web version, it may not be ticked for that app: the **Apps** tab, **Change**.
- `check` lists every profile and its mode.

</details>

<details>
<summary>"read only for this app"</summary>

- The profile is in **read** mode.
- The app wasn't allowed to change things when it logged in (the **Apps** tab).
- Read-only mode is on (the **Safety** tab, or `NEXTDNS_READ_ONLY`).

A mode set in the settings file or a hosting variable wins over the settings page.

</details>

<details>
<summary>"Which profile?"</summary>

You have several profiles and no default. Name one in your question, or set a default ([profiles.md](profiles.md#the-default-profile)).

</details>

<details>
<summary>"Too many changes in the last minute"</summary>

The brake (`NEXTDNS_CHANGE_LIMIT`, 30 a minute by default). Wait a minute. If an AI agent hit it on its own, check the **Changes** tab for what it was doing.

</details>

<details>
<summary>A new profile from the AI is in read mode</summary>

Profiles the AI makes are full for it, unless `NEXTDNS_PROFILES` lists them. Check that list.

</details>

## Changes and undo

<details>
<summary>A change doesn't show yet</summary>

NextDNS needs a few seconds before its DNS servers use it, and devices cache answers for a while (often a few minutes). `check_domain` makes a fresh query through the profile. Restarting the device's network, or waiting, clears its cache.

</details>

<details>
<summary>Undo says the profile "changed again since"</summary>

Something changed it after that change: the NextDNS dashboard, another app, or a later change. Undo anyway drops those later changes too: ask for it with force, or tick **Even if it changed again since** on the settings page. Or undo the later changes first, newest first.

</details>

<details>
<summary>"CONFIRMATION NEEDED" and nothing happened</summary>

That's the double confirmation working: deleting a profile, clearing logs and overwriting from a backup only happen on a second call with the code, after you say yes. Tell the AI yes. Codes last 5 minutes and work once; if it took longer, it asks again.

</details>

<details>
<summary>"Deleting profiles and clearing logs is turned off"</summary>

`NEXTDNS_ALLOW_DELETE=off`, or the box on the settings page (**Safety** tab) is unticked.

</details>

<details>
<summary>Some parts didn't come back after a restore or undo</summary>

NextDNS refused some values, for example a blocklist that no longer exists in its catalog. The answer lists them. Set those by hand, or ask the AI for the closest match (`catalog`).

</details>

## Logs and analytics

<details>
<summary>No logs, or `watch_logs` shows nothing</summary>

- Logs may be off for the profile: ask for its settings, or turn logs on (`profile_settings`).
- By default only useful queries show (A, AAAA and HTTPS, without repeats). Ask for raw logs to see every query.
- `watch_logs` only shows what happens while it watches: open the app or site during those seconds.

</details>

<details>
<summary>Analytics show nothing</summary>

There were no queries in that time, or logs are off (analytics need them). Try a longer time, like the last 30 days.

</details>

## Your AI app

<details>
<summary>The app doesn't show the tools</summary>

- Restart the app after adding the server.
- On a computer, use the full path of the command ([connect-your-ai.md](connect-your-ai.md#before-you-start-the-command-path)).
- Try the command yourself: `nextdns-agent-mcp stdio` should wait silently (Ctrl+C to stop). An error there is the real problem.

</details>

<details>
<summary>"Redirect not allowed" on login</summary>

The app's return address isn't on the list. Add its domain to `ALLOWED_REDIRECT_HOSTS` ([settings.md](settings.md)) and restart.

</details>

<details>
<summary>The login page says the link expired</summary>

Login links last 10 minutes. Start connecting again in the AI app.

</details>

<details>
<summary>The login page shows no profiles</summary>

The server has no working API key yet (open the settings page and paste it), or every profile is hidden.

</details>

<details>
<summary>The app was connected, now it isn't</summary>

Its key renews for 90 days; after that, or after **Disconnect** on the settings page, connect again.

</details>

## The web version

<details>
<summary>`serve` says "Set a passphrase first"</summary>

`LOGIN_PASSPHRASE` (6+ characters) or `LOGIN_HASH` must be set. On a computer: `nextdns-agent-mcp set-passphrase`.

</details>

<details>
<summary>Locked out of the settings page</summary>

Five wrong tries lock the login and the settings page for 15 minutes. Wait, then try again.

</details>

<details>
<summary>Forgot the passphrase</summary>

Set a new one (`set-passphrase`, or change `LOGIN_PASSPHRASE`) and restart.

</details>

<details>
<summary>Phones can't connect</summary>

The server needs a public HTTPS address, set as `PUBLIC_URL` (Render and Railway set it by themselves). `localhost` only works on the same computer. See [setup-computer.md](setup-computer.md#on-your-phone-through-a-tunnel) for a tunnel.

</details>

<details>
<summary>"Invalid Host header"</summary>

A proxy or tunnel sends a host name the server doesn't expect. Set `PUBLIC_URL` to the public address, and make the proxy pass the original `Host` header through.

</details>

<details>
<summary>Settings, logins or backups vanish after a restart</summary>

The data folder isn't on a disk that survives restarts. Add a volume at `/data` ([setup-hosting.md](setup-hosting.md)).

</details>

<details>
<summary>"Address already in use" when starting `serve`</summary>

Something else uses port 8766, maybe another copy of the server. Stop it, or set `PORT` to another number.

</details>

## Still stuck?

Open an [issue](https://github.com/s17sh70x2jfl031ag/NextDNS-Agent-MCP/issues/new?template=bug_report.yml) with what you asked, what happened, how you run it, and `nextdns-agent-mcp version`. Leave out your API key, passphrase, profile IDs and anything from your logs.
