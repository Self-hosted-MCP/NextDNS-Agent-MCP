# Changelog

## 0.8.1 (2026-10-20)

- The project moved to the [Self-hosted MCP](https://github.com/Self-hosted-MCP) organisation on GitHub. Old links to the repository redirect to the new one.
- The ready-made Docker image is now `ghcr.io/self-hosted-mcp/nextdns-agent-mcp`. If you run the old image name, switch to this one to keep getting updates.
- `scripts/update.sh` follows GitHub's redirects.

## 0.8.0 (2026-10-16)

- The license is now the Apache License 2.0, with a patent grant and clear rules for the NOTICE file.
- NOTICE rewritten for Apache: the license in plain words, not made by NextDNS, credit and third-party licenses.

## 0.7.0 (2026-10-16)

- Update check, off by default: once a day the server asks GitHub which release is newest (nothing about you is sent) and says so in the `profiles` tool and on the settings page. Turn it on in the About tab or with `UPDATE_CHECK=on`.
- `nextdns-agent-mcp update` installs the newest official release with uv, or says you're up to date. The docs show how to run it every week on Mac, Linux and Windows.
- `scripts/update.sh` updates a Docker Compose copy to the newest release; forks can follow releases by themselves with the `update-from-releases` workflow (`AUTO_UPDATE=on`).

## 0.6.3 (2026-10-16)

- The connect guide covers 16 more AI apps and agents, each with its settings from the app's own docs: Goose, Cline, Roo Code, Continue, Windsurf (Devin Desktop), Zed, LM Studio, OpenCode, Kiro, GitHub Copilot CLI, Amp, Warp, JetBrains AI Assistant, Qwen Code, Crush and Augment Code.

## 0.6.2 (2026-10-16)

- Docs at the level of Selfhost-Remote-Mail-MCP: a full security policy (what to report, how, timelines, scope), contributing guide, AGENTS.md (the code, the rules that must never break, setting it up for someone), a NOTICE file (license in plain words, not made by NextDNS, third-party licenses), and longer guides for the FAQ, troubleshooting, safety (what it doesn't protect against, what to do if something goes wrong, checked against MCP security guidance), privacy (what leaves your server, encryption, every stored file), every setting, updates (by hand, by itself, going back), languages and the Claude Desktop extension.
- `.env.example` lists every setting, with comments. The bug form asks for more details.
- NOTICE ships in the package, the Docker image and the extension.
- The Railway one-click template is published: railway.com/deploy/nextdns-agent-mcp.

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
