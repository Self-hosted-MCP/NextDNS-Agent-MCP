# Security policy

This server holds an API key that can change everything in someone's NextDNS account: what their devices block, and what they let through. Security reports are very welcome.

## Supported versions

Only the newest release gets security fixes. Every way of running it (the Docker image, the Claude Desktop extension, `uv tool`) follows published releases, so updating is the fix. See [docs/updates.md](docs/updates.md).

| Version | Security fixes |
|---|---|
| Latest release ([see Releases](https://github.com/Self-hosted-MCP/NextDNS-Agent-MCP/releases/latest)) | Yes |
| Any older version | No, please update |

## Reporting a problem

Please **don't** open a public issue, discussion or pull request for a security problem.

1. Go to the **Security** tab of this repository and click **[Report a vulnerability](https://github.com/Self-hosted-MCP/NextDNS-Agent-MCP/security/advisories/new)**. Only the maintainer sees it.
2. Tell me:
   - the version (`nextdns-agent-mcp version`, or the About tab on the settings page) and how you run it (computer, extension, Docker, hosting company)
   - what you found and which part of the code it's in, if you know
   - the steps to reproduce it
   - what an attacker could do with it, and what they need first (for example the passphrase, or access to the computer)
3. Remove real API keys, passphrases, tokens, profile IDs and anything from DNS logs. Use a test NextDNS profile if you need one.

There's no email contact. Use private reporting.

## What happens next

| When | What |
|---|---|
| Within 3 days | You get a first answer saying the report arrived |
| Within 10 days | I confirm the problem (or explain why it isn't one) and agree on a plan |
| Usually within 30 days | A fixed release is published |
| After the release | The advisory is published, with a CVE when it's useful |

This is a project run in spare time, so a date can slip. If it does, you'll hear why. Please keep the problem private until the fixed release is out, or until 90 days have passed, whichever comes first.

## Credit

If you'd like, you're named in the published advisory and in [CHANGELOG.md](CHANGELOG.md). Tell me the name or GitHub account to use, or say you'd rather stay anonymous. There's no paid bug bounty.

## Testing in good faith

If you follow this policy, I won't take any action against you for your research. Please:

- test only on a server and a NextDNS account that you own, or have permission to test
- never change or read other people's NextDNS profiles or logs
- stop and report as soon as you see someone else's data
- don't run denial-of-service tests against someone else's server, or against NextDNS

## In scope

- Anything that lets someone without the passphrase use the server, its settings page or its tools.
- Any way to change a profile in **read** mode, see a **hidden** profile, reach a profile an app wasn't given at login, or change things when the app wasn't allowed to, or when read-only mode is on. See [AGENTS.md](AGENTS.md#rules-that-must-never-break).
- Any way to delete a profile, clear logs or overwrite a profile without the double confirmation, or to reuse a confirmation code.
- Ways to make a change that doesn't land in the change log, or an undo that doesn't put back what was there.
- Leaks of the API key, passphrase, tokens or DNS logs (server logs, error messages, tool answers to the wrong app).
- Ways for data from NextDNS (a domain name, a log entry, a blocklist description) to make the server itself do something (not the AI model, which is covered by [docs/safety.md](docs/safety.md)).
- Problems in how the server stores the API key, logins, sessions, the change log or backups in the data folder.

## Out of scope

- An AI model following instructions hidden in a domain name, log entry or description. That's prompt injection, a known limit of today's AI models. The server's defences are in [docs/safety.md](docs/safety.md), and improvements to them are welcome as normal issues.
- A user asking the AI to do something harmful to their own profiles, after the confirmations.
- Weak passphrases chosen by a user, or a settings file or API key shared by its owner.
- Problems that need someone who already controls your computer or server.
- Problems in NextDNS itself, your hosting company or your AI app. Please report those to them.
- Problems in a dependency that this project doesn't use in a harmful way.
- Missing security headers or reports from automated scanners without a real attack that works.

## Keeping your own server safe

- Update when a new release comes out.
- Use a passphrase nobody can guess. Six characters is the minimum, more is better on a server anyone can reach.
- Hide the profiles the AI doesn't need, and make your important ones read only until you trust it.
- Give each AI app only the profiles it needs, and check the **Apps** and **Changes** tabs on the settings page now and then.
- If the API key may have leaked, make a new one at my.nextdns.io/account: the old one stops working at once.
- More in [docs/safety.md](docs/safety.md) and [docs/privacy.md](docs/privacy.md).
