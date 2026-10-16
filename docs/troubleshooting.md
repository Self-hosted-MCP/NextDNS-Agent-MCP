# Troubleshooting

**"NextDNS refused the API key".** Copy the key again from the bottom of [my.nextdns.io/account](https://my.nextdns.io/account). `uv run nextdns-agent-mcp check` tests it.

**The AI says a profile doesn't exist.** It may be hidden (profile modes), or not ticked for that app when it connected. Check the Profiles and Apps tabs on the settings page.

**"read only for this app".** The profile is set to read, the app wasn't allowed to change things at login, or read-only mode is on.

**A change doesn't show yet.** NextDNS needs a few seconds before its DNS servers use it. `check_domain` says so too.

**No logs, or `watch_logs` shows nothing.** Logs may be off for the profile: `profile(section='settings')`. By default only useful queries show; `raw=true` shows all.

**The login page says the link expired.** Links last 10 minutes. Start connecting again in the AI app.

**Locked out of the settings page.** Five wrong tries lock it for 15 minutes.

**Forgot the passphrase.** Set a new one (`set-passphrase`, or change `LOGIN_PASSPHRASE`) and restart. Every signed-in browser is signed out.

**The saved API key can't be read after a move.** `NEXTDNS_SECRET_KEY` changed or the `secret.key` file was lost. Paste the key again on the settings page.
