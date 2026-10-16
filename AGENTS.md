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
