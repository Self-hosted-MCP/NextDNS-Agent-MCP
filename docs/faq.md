# Questions people ask

**Is this made by NextDNS?**
No. It's an independent open-source project that uses NextDNS's public API with your own key.

**Does it work with any AI app, or only Claude?**
Any app that speaks MCP: Claude (desktop, web, phone, Claude Code), ChatGPT, Codex, Cursor, VS Code, Gemini CLI, OpenClaw, Hermes Agent and others. See [connect-your-ai.md](connect-your-ai.md).

**What can't it do?**
What the NextDNS API can't: change your account itself (email, password, billing), manage the NextDNS apps on your devices, or rename devices. It also only handles DNS: it can't control your router, Wi-Fi or apps that skip DNS.

**Does it cost anything?**
The software is free (MIT). NextDNS has its own plans. Running it on your computer is free; a hosting company costs a few dollars a month.

**Do I need the web version?**
Only for your phone, the Claude or ChatGPT website, or the settings page. On one computer, `stdio` or the Claude Desktop extension is enough.

**Can the AI break my internet?**
It could turn off a protection or block a site everyone needs, if you ask for it or it misunderstands. Every change can be undone (*"undo that"*), and you can make profiles read only or hidden. Deleting things always asks you twice. See [safety.md](safety.md).

**Can it see my browsing?**
It can read your NextDNS logs (the domains your devices looked up) when you ask it to, like the NextDNS dashboard can. Hide a profile to keep its logs away from the AI, or turn logs off in NextDNS.

**Why does `check_domain` show up in my logs?**
It makes a real DNS query through the profile, to see exactly what a device would get.

**A change doesn't work yet.**
NextDNS needs a few seconds before its DNS servers use it, and your device may still have the old answer cached for a while.

**Can two AI apps use it at the same time?**
Yes. On the web version each app has its own login and its own choice of profiles. On one computer, every app shares the same settings and change log.

**Where's my API key stored?**
In your settings file, a hosting variable, or (pasted on the settings page) encrypted in the data folder. It goes only to NextDNS. See [privacy.md](privacy.md).

**I lost the passphrase.**
Set a new one (`nextdns-agent-mcp set-passphrase`, or change `LOGIN_PASSPHRASE`) and restart. Browsers are signed out; connected apps stay connected.

**Can I use it for several NextDNS accounts?**
One API key per server. Run a second copy with its own settings file (`NEXTDNS_ENV_FILE`) and data folder (`NEXTDNS_DATA_DIR`), or with `NEXTDNS_CONFIG_DIR`.

**Is there a limit on the NextDNS API?**
NextDNS doesn't publish one. The server waits and tries again when NextDNS says it's busy, and limits itself to 30 changes a minute.
