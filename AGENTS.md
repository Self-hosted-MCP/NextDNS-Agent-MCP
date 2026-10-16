# Guide for AI agents and contributors

NextDNS-Agent-MCP is an MCP server for the NextDNS API. MIT. Not made by NextDNS.

## Layout

- `src/nextdns_agent_mcp/server.py`: settings, the change log and undo, every tool, the commands (`stdio`, `serve`, `check`, `set-passphrase`, `version`).
- `api.py`: the NextDNS API client (errors can come with HTTP 200: always check `errors`), the live log stream and DNS-over-HTTPS test queries.
- `auth.py`: the passphrase OAuth server for AI apps and the settings-page sessions. `web.py`: the routes. `pages.py`: the HTML (no scripts, strict CSP, every value through `esc()`).
- `store.py`: owner-only files, locks, encryption, passphrase hashing. `charts.py`: PNG charts with Pillow. `i18n.py` and `locales/`: ready for translations, English only so far.

There is no database: small JSON files in the data folder.

## Rules

- Every change goes through `changing()` so it lands in the change log and can be undone.
- Anything that deletes, or overwrites a whole profile, goes through `double_check()`.
- Check modes with `find_profile()` and `need_change()`; never call the API for a profile the app may not see.
- Tool answers are plain English for the AI; page texts go through `_()`.
- Tests use the fake NextDNS in `tests/conftest.py`: `uv run pytest -q`. Never test against a real profile you care about.

## Deploying for a user

When a user asks you to set this up for them:

1. **Ask where:** their computer (any AI app on it), the Claude Desktop extension, a hosting company (Render, Railway, any Docker host), or their own server. Guides: `docs/setup-*.md`, `docs/claude-desktop-extension.md`.
2. **The API key:** ask the user to copy it from the bottom of my.nextdns.io/account. Put it only in the settings file, a hosting variable, or the settings page. Never in a repository, a chat log you keep, or a command line others can see.
3. **On a computer:** `uv tool install git+https://github.com/s17sh70x2jfl031ag/NextDNS-Agent-MCP`, write `~/.config/nextdns-agent-mcp/.env` (mode 600) with `NEXTDNS_API_KEY`, run `nextdns-agent-mcp check`.
4. **Ask which profiles** the AI may change, read, or never see, and set `NEXTDNS_PROFILES` (see `docs/profiles.md`).
5. **Web version:** set `LOGIN_PASSPHRASE` (6+ characters, the user chooses it) and `NEXTDNS_SECRET_KEY` (random, kept), a disk at `/data`, and `PUBLIC_URL` unless the host sets it. Check `/health`, then have the user open `/settings`.
6. **Connect the user's AI app** (`docs/connect-your-ai.md`) and ask it to run `profiles`.
7. **Don't test changes on the user's real profiles.** Make a test profile, or use read-only tools.
