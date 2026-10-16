# Changelog

## 0.6.1 (2026-10-16)

- Full docs, for any AI app: a new README, and guides for the Claude Desktop extension, setup on a computer, a hosting company and your own server, connecting 10 AI apps and any other MCP app, profiles and apps, examples, undo and backups, how it works, privacy, safety, settings and the settings page, updates, languages, FAQ, troubleshooting and roadmap. Screenshots and example charts.
- Issue forms (bug, question) and a private security report link. A checklist in AGENTS.md for AI agents setting it up for someone.
- Tests check every link and heading anchor in the docs.

## 0.6.0 (2026-10-16)

- Docs: tools (from the tools' own descriptions), safety, settings, running it, troubleshooting.
- Repo files: AGENTS.md, SECURITY.md, CONTRIBUTING.md, CITATION.cff.

## 0.5.0 (2026-10-16)

- Easy hosting: `Dockerfile` (amd64 and arm64), `docker-compose.yml` with Caddy for HTTPS, `render.yaml`, `railway.json`.
- Claude Desktop extension (`.mcpb`): paste the API key, choose read only or allow deletes. Checked with Anthropic's validator.
- GitHub workflows: tests on Python 3.11 and 3.14; on each release, the Docker image on GHCR and the extension attached to the release.
- README: every way to run it, and how to get the API key.
- New look: dark blue with an amber accent (pages, icon, charts).

## 0.4.0 (2026-10-16)

- `check_domain`: is a domain blocked, and why. A real query through the profile, plus the lists and the log.
- `watch_logs`: the live log for 5 to 120 seconds.
- `chart`: any analytics report as a PNG, lines over time or bars.
- `compare_profiles`: what differs between two profiles.
- Backups: `backup`, `backups`, `restore_backup` (overwriting asks twice; or make a new profile from it). The settings page has a Backups tab: back up now, download, add a file, restore, delete.
- The settings and login pages explain how to get the API key, with links to the NextDNS account page and the official API docs.

## 0.3.0 (2026-10-16)

- Web version (`serve`): AI apps on your phone and claude.ai connect with a login page and your passphrase (6+ characters). Each app gets only the profiles you tick, with or without changes.
- Settings page: API key (stored encrypted), profile modes, connected apps (change or disconnect), the change log with Undo buttons, safety switches, light and dark.
- The AI may now do everything by default (profiles are full unless set otherwise).
- Deleting a profile, clearing logs, and undoing the creation of a profile need a double confirmation: a one-time code the AI only gets to use after asking you. `NEXTDNS_ALLOW_DELETE` is now on by default and turns these off when set to off.
- `set-passphrase` command. Pages are ready for other languages (English only for now).

## 0.2.0 (2026-10-16)

- New tools: `security`, `parental_control` (with recreation time), `rewrites`, `profile_settings`, `create_profile`, `delete_profile`, `clear_logs`, `changes`, `undo`.
- Every change is recorded with the state before and after; `undo` puts it back, and stops if the profile changed again since.
- Deleting profiles and clearing logs need `NEXTDNS_ALLOW_DELETE=on` and the profile's exact name.
- A limit of changes per minute (`NEXTDNS_CHANGE_LIMIT`, default 30).

## 0.1.0 (2026-10-16)

- First version, for one AI app on your computer (stdio): `profiles`, `profile`, `catalog`, `analytics`, `logs`, `list_entries`, `privacy`.
- Profile modes: full, read or hidden. Server-wide read-only mode.
