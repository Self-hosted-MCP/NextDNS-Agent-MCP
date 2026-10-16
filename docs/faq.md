# Questions people ask

<details>
<summary><b>Is it free?</b></summary>

The software is free and open source (Apache License 2.0). Running it on your own computer is free. A hosting company costs a few dollars a month, paid to them. NextDNS and the AI app you use have their own plans.

</details>

<details>
<summary><b>Is this made by NextDNS?</b></summary>

No. Not made by or affiliated with NextDNS. It uses the public NextDNS API with your own API key.

</details>

<details>
<summary><b>Does it work with my AI app, or only Claude?</b></summary>

Any app that speaks MCP: Claude (desktop, website, phone, Claude Code), ChatGPT, Codex, Cursor, VS Code, Gemini CLI, OpenClaw, Hermes Agent and others. See [connect-your-ai.md](connect-your-ai.md).

</details>

<details>
<summary><b>Who can see my DNS logs?</b></summary>

NextDNS (as always), and the AI app you connect, for the logs and stats it reads when you ask. Nobody else: the authors of this project get nothing, no account, no tracking. Hide a profile to keep its logs away from the AI. Details in [privacy.md](privacy.md).

</details>

<details>
<summary><b>Can the AI change things without asking me?</b></summary>

It changes things when you ask it to, like the NextDNS dashboard would. It can't delete a profile, clear logs or overwrite a profile from a backup without asking you first and getting a yes (a one-time code it only gets after asking). You can also make profiles read only, hide them, turn read-only mode on, or set tools to "Always ask" in your AI app. See [safety.md](safety.md).

</details>

<details>
<summary><b>What if it changes the wrong thing?</b></summary>

Ask *"undo that"*, or press **Undo** on the settings page. Every change is saved with how things were before. See [undo-and-backups.md](undo-and-backups.md).

</details>

<details>
<summary><b>Can it break my internet?</b></summary>

It could turn off a protection or block a site everyone needs, if you ask for it or it misunderstands. Changes reach NextDNS within seconds, and so does the undo. Try things on a test profile first, and keep the profiles of other people's devices hidden or read only.

</details>

<details>
<summary><b>What can't it do?</b></summary>

What the NextDNS API can't: change your account itself (email, password, billing), manage the NextDNS apps on your devices, or rename devices. It only handles DNS: it can't control your router, Wi-Fi or apps that skip DNS.

</details>

<details>
<summary><b>Can I use several profiles?</b></summary>

Yes, all the profiles in your account. Each gets a mode (full, read only, hidden), and each AI app on the web version gets only the ones you tick. See [profiles.md](profiles.md).

</details>

<details>
<summary><b>Can I use several NextDNS accounts?</b></summary>

One API key per server. Run a second copy with its own settings file and data folder: set `NEXTDNS_CONFIG_DIR` to another folder for it.

</details>

<details>
<summary><b>Does it keep a copy of my logs?</b></summary>

No. Logs and analytics stay at NextDNS. The server keeps only small files: settings, the change log (copies of profile settings and lists, before and after each change), backups you make, and fingerprints of login keys.

</details>

<details>
<summary><b>Why does `check_domain` show up in my logs?</b></summary>

It makes a real DNS query through the profile, to see exactly what a device would get.

</details>

<details>
<summary><b>A change doesn't work yet.</b></summary>

NextDNS needs a few seconds before its DNS servers use it, and your device may still have the old answer cached for a while.

</details>

<details>
<summary><b>What happens if my computer is off?</b></summary>

On your computer, the server only runs while the computer (and your AI app) does. Your NextDNS filtering keeps working: that's NextDNS, not this server. For your phone at any time, run it on a [hosting company](setup-hosting.md).

</details>

<details>
<summary><b>Do I need the web version?</b></summary>

Only for your phone, the Claude or ChatGPT website, or the settings page. On one computer, `stdio` or the Claude Desktop extension is enough.

</details>

<details>
<summary><b>Can two AI apps use it at the same time?</b></summary>

Yes. On the web version each app has its own login and its own choice of profiles. On one computer, every app shares the same settings and change log.

</details>

<details>
<summary><b>Where's my API key stored?</b></summary>

In your settings file, a hosting variable, or (pasted on the settings page) encrypted in the data folder. It goes only to NextDNS, and your AI app never sees it. See [privacy.md](privacy.md).

</details>

<details>
<summary><b>I think my API key leaked.</b></summary>

Make a new one at my.nextdns.io/account: the old one stops working at once. Then put the new one in your settings file or on the settings page.

</details>

<details>
<summary><b>I lost the passphrase.</b></summary>

Set a new one: `nextdns-agent-mcp set-passphrase` on a computer, or change `LOGIN_PASSPHRASE` on your host, then restart. Browsers are signed out; connected apps stay connected (disconnect them on the settings page if you want).

</details>

<details>
<summary><b>How long is the passphrase?</b></summary>

6 characters or more. Five wrong tries lock the login for 15 minutes, which keeps guessing slow. On a server anyone can reach, longer is better.

</details>

<details>
<summary><b>Is there a limit on the NextDNS API?</b></summary>

NextDNS doesn't publish one. The server waits and tries again when NextDNS says it's busy, and limits itself to 30 changes a minute.

</details>

<details>
<summary><b>How do I update?</b></summary>

See [updates.md](updates.md). Updates never touch your settings, change log or backups.

</details>

<details>
<summary><b>How do I remove it?</b></summary>

Remove it from your AI app, then: on a computer `uv tool uninstall nextdns-agent-mcp` and delete `~/.config/nextdns-agent-mcp`; on a host, delete the service and its disk. Your NextDNS account isn't touched. Delete the API key at my.nextdns.io/account if you made one just for this.

</details>

<details>
<summary><b>Is it safe to make it public on the internet?</b></summary>

It's built for that: a passphrase, a login per app, profiles per app, short-lived keys, and a lockout after wrong tries. Read [safety.md](safety.md) and keep it updated.

</details>
