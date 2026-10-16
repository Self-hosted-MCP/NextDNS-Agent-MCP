# Contributing

Thanks for wanting to help. NextDNS-Agent-MCP is free and open source under the [Apache License 2.0](LICENSE). Bug reports, fixes, clearer docs and translations are all welcome.

## Reporting a problem

Click **New issue** on GitHub and pick a form:

| Form | Use it when |
|---|---|
| **Something doesn't work** | You hit a bug or an error message |
| **Question or idea** | You want to know how to do something, or have an idea |
| **Report a security problem, privately** | Someone could misuse the server. Only the maintainer sees it |

Each form asks for what's needed to help you, such as how you run the server and which AI app you use. There's no email contact: the forms and private reporting cover everything, and they keep the conversation in one place.

**Remove your API key, passphrase, profile IDs and anything from your DNS logs** before posting. For security problems, don't open an issue: follow [SECURITY.md](SECURITY.md).

## Changing the code

1. Read [AGENTS.md](AGENTS.md). It explains the code and the rules that must never break, such as "every change goes in the change log".
2. Install the tools: `uv sync`.
3. Make your change, with a test in `tests/`. The tests use a fake NextDNS (`tests/conftest.py`); never use a real account in tests.
4. Run `uv run pytest -q`. Everything must pass. The tests also check that every tool is in `docs/tools.md` and in the extension's manifest, that every setting is in `docs/settings.md`, and that every link in the docs works.
5. If people will notice the change, update the matching page in `docs/` and add a line to [CHANGELOG.md](CHANGELOG.md).
6. Open a pull request saying what changed and why.

Trying a change against a real account? Make a test profile in NextDNS, set your real profiles to `hidden` (`NEXTDNS_PROFILES`), and use a separate config folder (`NEXTDNS_CONFIG_DIR`).

## Releases (maintainers)

1. Set the new version in `pyproject.toml` and `CITATION.cff`, and move the notes in [CHANGELOG.md](CHANGELOG.md) under it with the date.
2. Run the tests, push to `main`, wait for the **Tests** workflow to pass.
3. Tag it `vX.Y.Z` and publish a GitHub Release with the changelog notes.

Publishing the release builds the Docker image (`ghcr.io/s17sh70x2jfl031ag/nextdns-agent-mcp`, tags: version, major.minor, `latest`) and the Claude Desktop extension, checked with Anthropic's validator and attached to the release. Nothing reaches the image or the extension before that.

## Translations

The web pages are ready for other languages: texts go through `_()` and a language is `src/nextdns_agent_mcp/locales/<code>.json`. See [docs/languages.md](docs/languages.md). Natural, everyday wording beats word-for-word.

## Writing docs

The docs are for people who have never used a terminal. Use short sentences and everyday words, explain any technical word the first time, and show what the reader should see when a step works. No em dashes. Don't write that something was tested unless it was.

## Credit

By contributing you agree that your work is shared under the [Apache License 2.0](LICENSE) (its section 5 covers contributions). Keep the original credit (`LICENSE`, `NOTICE`, `CITATION.cff`) and add yourself to the changelog entry if you like.
