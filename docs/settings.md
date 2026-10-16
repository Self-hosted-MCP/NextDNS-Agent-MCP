# Every setting

You can change the important things on the **settings page** (web version), and everything in the **settings file** or hosting variables. Every setting is optional except the API key (and, for the web version, a passphrase).

## Where settings come from

Each place wins over the one before:

1. the **settings page** of the web version (profiles, default profile, read-only, allow deletes, the mode for profiles not listed, and the API key),
2. the **settings file**: `~/.config/nextdns-agent-mcp/.env` (or `NEXTDNS_ENV_FILE`), one `NAME=value` per line, `#` for comments,
3. **environment variables**: a hosting company's "Variables" page, Docker's `-e`, or an AI app's `env` block.

A setting fixed in 2 or 3 shows on the settings page, but can only be changed where it was set. A template with every setting: [`.env.example`](../.env.example).

## The settings page

Open `/settings` on the web version (`http://localhost:8766/settings` on a computer) and sign in with your passphrase. Tick **Remember this device** to stay signed in for 90 days; otherwise it lasts until you close the browser, 12 hours at most.

| Tab | What you do there |
|---|---|
| **API key** | Paste your NextDNS API key, with steps and links to find it. **Test and save** checks it first. Stored encrypted. **Remove the key** deletes it |
| **Profiles** | A mode for each profile (read and change, read only, hidden), and the default profile |
| **Apps** | The AI apps connected over the internet: which profiles each may use, whether it may change things, **Disconnect** |
| **Changes** | The change log, newest first, with **Undo** |
| **Backups** | Back up a profile now, download, add a backup file, restore, make a new profile from one, delete |
| **Safety** | Read-only mode, allow deletes (always asked twice), the mode for profiles not listed |
| **About** | The version, the address AI apps connect to, **Sign out** |

The round button at the top switches between light, dark and your device's look.

## NextDNS and profiles

| Setting | What it does | Default |
|---|---|---|
| `NEXTDNS_API_KEY` | Your NextDNS API key (bottom of my.nextdns.io/account) | none |
| `NEXTDNS_PROFILES` | Mode per profile: `id-or-name=full,other=read,third=hidden` ([profiles.md](profiles.md)) | none |
| `NEXTDNS_DEFAULT_MODE` | Mode for profiles not listed: full, read or hidden | full |
| `NEXTDNS_DEFAULT_PROFILE` | The profile used when the AI names none (ID or name) | none |

## Safety

| Setting | What it does | Default |
|---|---|---|
| `NEXTDNS_READ_ONLY` | on: nothing can be changed, by any app | off |
| `NEXTDNS_ALLOW_DELETE` | off: never delete profiles or clear logs. On, they're always asked twice | on |
| `NEXTDNS_CHANGE_LIMIT` | Changes allowed per minute | 30 |
| `NEXTDNS_APP_NAME` | The name in the change log for apps on this computer | AI app |

`on`, `true`, `yes` and `1` all mean on.

## Updates

| Setting | What it does | Default |
|---|---|---|
| `UPDATE_CHECK` | on: once a day, ask GitHub which release is newest, and say so in the `profiles` tool and on the settings page (About tab). Sends nothing about you. Also a switch on the settings page | off |

## Web version (`serve`)

| Setting | What it does | Default |
|---|---|---|
| `LOGIN_PASSPHRASE` | Passphrase for the login and settings pages, 6+ characters | none |
| `LOGIN_HASH` | The same, stored as a hash (`nextdns-agent-mcp set-passphrase` writes it). Wins over `LOGIN_PASSPHRASE` | none |
| `PUBLIC_URL` | The HTTPS address it's reached at, without `/mcp` | Render's or Railway's address, else `http://localhost:8766` |
| `HOST` | The network address it listens on | 127.0.0.1 (Docker: 0.0.0.0) |
| `PORT` | The port | 8766 |
| `NEXTDNS_SECRET_KEY` | Encrypts the API key saved on the page. Set it on hosting; never change it | a random `secret.key` file |
| `ALLOWED_REDIRECT_HOSTS` | AI apps allowed to receive a login, comma-separated (localhost always is) | claude.ai, claude.com, chatgpt.com, openai.com, vscode.dev |
| `SETTINGS_PAGE` | off: no settings page (AI app logins still work) | on |

`RENDER_EXTERNAL_URL` and `RAILWAY_PUBLIC_DOMAIN` are set by Render and Railway themselves; the server reads them to find its address.

## Folders

| Setting | What it does | Default |
|---|---|---|
| `NEXTDNS_CONFIG_DIR` | The folder for the settings file and data | `~/.config/nextdns-agent-mcp` (Docker: `/data`) |
| `NEXTDNS_ENV_FILE` | Another settings file | `<config folder>/.env` |
| `NEXTDNS_DATA_DIR` | The data folder | `<config folder>/state` (Docker: `/data`) |

These three are read from the environment only, not from the settings file.

## Files in your config folder

| File | What it is |
|---|---|
| `.env` | The settings file. Keep it owner-only (`chmod 600`); the server warns if others can read it |
| `state/` | The data folder: the saved API key (encrypted), logins, the change log, backups. See [privacy.md](privacy.md#what-the-server-keeps) |
