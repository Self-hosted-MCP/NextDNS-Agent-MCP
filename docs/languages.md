# Languages

## Talking to the AI

**The AI talks to you in your language already.** Tool answers are in English, written for the AI, and the server tells it to speak to you in yours. Ask in Portuguese, Japanese or any other language: it works the same.

## The web pages

The login and settings pages are in **English** for now.

They're built for translations:

- Every text a person reads on a page goes through one function, `_("...")`, in `src/nextdns_agent_mcp/pages.py`.
- A language is one file, `src/nextdns_agent_mcp/locales/<code>.json`, mapping each English text to its translation:

  ```json
  {
    "Passphrase": "Frase-passe",
    "Allow access": "Permitir acesso"
  }
  ```

- Texts missing from a file stay in English, so a half-done language still works.
- `{placeholders}` (like `{app}`) and HTML tags (like `<b>`) must stay exactly as they are.

The pages will pick the language from the browser once languages ship. Choosing the language on the page, and the 20 languages of Selfhost-Remote-Mail-MCP, are on the [roadmap](roadmap.md).

## Add a language

Open a [question](https://github.com/s17sh70x2jfl031ag/NextDNS-Agent-MCP/issues/new?template=question.yml) to say which one, or send a pull request with the file.

An AI coding agent can make it. Ask it:

> Collect every text inside `_("...")` in `src/nextdns_agent_mcp/pages.py` and translate them into `src/nextdns_agent_mcp/locales/<code>.json`, keeping `{placeholders}` and HTML tags exactly as they are. Use natural, everyday wording.

Natural, everyday wording beats word-for-word.
