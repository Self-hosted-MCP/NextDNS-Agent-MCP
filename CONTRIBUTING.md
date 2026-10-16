# Contributing

Thanks for helping.

- **A problem:** open an issue with what you asked the AI, what happened and the version (`nextdns-agent-mcp version`). Leave out your API key and profile IDs.
- **A fix or a feature:** read [AGENTS.md](AGENTS.md), add a test with the fake NextDNS, and run `uv run pytest -q`.
- **Releases:** a version in `pyproject.toml`, a `CHANGELOG.md` entry, a `vX.Y.Z` tag and a GitHub Release. The release builds the Docker image and the `.mcpb` file.
