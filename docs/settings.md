# Settings

You can change the important things on the **settings page** (web version), and everything in the **settings file** or hosting variables.

## The settings page

Open `/settings` on the web version (`http://localhost:8766/settings` on a computer) and sign in with your passphrase.

| Tab | What you do there |
|---|---|
| **API key** | Paste your NextDNS API key, with steps and links to find it. **Test and save** checks it first. Stored encrypted. |
| **Profiles** | A mode for each profile (read and change, read only, hidden), and the default profile |
| **Apps** | The AI apps connected over the internet: which profiles each may use, whether it may change things, **Disconnect** |
| **Changes** | The change log, newest first, with **Undo** |
| **Backups** | Back up a profile now, download, add a backup file, restore, make a new profile from one, delete |
| **Safety** | Read-only mode, allow deletes (always asked twice), the mode for profiles not listed |
| **About** | The version, the address AI apps connect to, **Sign out** |

The round button at the top switches between light, dark and your device's look.

## Where settings come from


Each place wins over the one before:

1. the **settings page** of the web version (profiles, default profile, read-only, allow deletes, and the API key),
2. the **settings file**: `~/.config/nextdns-agent-mcp/.env` (or `NEXTDNS_ENV_FILE`),
3. **environment variables** (hosting dashboards).

A setting fixed in 2 or 3 shows on the settings page, but can only be changed where it was set.

| Setting | What it does | Default |
|---|---|---|
| `NEXTDNS_API_KEY` | Your NextDNS API key (bottom of my.nextdns.io/account) | none |
| `NEXTDNS_PROFILES` | Mode per profile: `id-or-name=full,other=read,third=hidden` | none |
| `NEXTDNS_DEFAULT_MODE` | Mode for profiles not listed: full, read or hidden | full |
| `NEXTDNS_DEFAULT_PROFILE` | The profile used when the AI names none | none |
| `NEXTDNS_READ_ONLY` | on: nothing can be changed | off |
| `NEXTDNS_ALLOW_DELETE` | off: never delete profiles or clear logs | on |
| `NEXTDNS_CHANGE_LIMIT` | Changes allowed per minute | 30 |
| `NEXTDNS_APP_NAME` | Name in the change log for the app on this computer | AI app |
| `NEXTDNS_CONFIG_DIR` | Folder for the settings file and data | `~/.config/nextdns-agent-mcp` |
| `NEXTDNS_DATA_DIR` | Folder for the change log, logins and backups | `<config folder>/state` |

Web version only:

| Setting | What it does | Default |
|---|---|---|
| `LOGIN_PASSPHRASE` | Passphrase for the login and settings pages, 6+ characters | none |
| `LOGIN_HASH` | The same, stored as a hash (`nextdns-agent-mcp set-passphrase` writes it) | none |
| `PUBLIC_URL` | The HTTPS address it's reached at | Render or Railway address, or localhost |
| `HOST`, `PORT` | Where it listens | 127.0.0.1, 8766 (Docker: 0.0.0.0) |
| `NEXTDNS_SECRET_KEY` | Encrypts the API key saved on the page. Set it on hosting; never change it | a random file |
| `ALLOWED_REDIRECT_HOSTS` | AI apps allowed to log in (localhost always is) | claude.ai, claude.com, chatgpt.com, openai.com, vscode.dev |
| `SETTINGS_PAGE` | off: no settings page (logins still work) | on |
