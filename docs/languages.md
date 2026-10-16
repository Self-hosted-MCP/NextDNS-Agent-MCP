# Languages

**The AI talks to you in your language already.** Tool answers are in English, written for the AI, and it speaks to you in whatever language you use.

**The web pages** (login and settings) are in English for now. They are ready for translations: every text on them goes through one function, and a language is one file, `src/nextdns_agent_mcp/locales/<code>.json`, mapping each English text to its translation. Texts missing from a file stay in English, so a half-done language still works.

Want your language? Open a [question](https://github.com/s17sh70x2jfl031ag/NextDNS-Agent-MCP/issues/new?template=question.yml), or send a pull request with a file. An AI coding agent can make one: ask it to collect every text inside `_("...")` in `pages.py` and translate them into `locales/<code>.json`, keeping `{placeholders}` and HTML tags exactly as they are.
