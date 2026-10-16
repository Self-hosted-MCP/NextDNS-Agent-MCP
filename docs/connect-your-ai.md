# Connect your AI app

Any app that speaks MCP can use this server. There are two ways it can reach it:

- **On the same computer (`stdio`).** The app starts its own small copy of the server. No login and no web address needed. You need [the computer setup](setup-computer.md) done (the API key in the settings file).
- **Over the internet (`serve`).** The app connects to `https://your-address/mcp` and you log in once with your passphrase, ticking which profiles it may use. You need [a hosting company](setup-hosting.md), [your own server](setup-own-server.md), or your computer with a tunnel.

```mermaid
flowchart LR
    subgraph computer["On the same computer: stdio"]
        A1["Claude Desktop, Claude Code, Codex,<br/>Cursor, VS Code, Gemini CLI, OpenClaw,<br/>Hermes, Goose, Cline, Zed, Kiro, ..."] -->|"starts it"| S1["NextDNS-Agent-MCP"]
    end
    subgraph internet["Over the internet: serve"]
        A2["Claude website and phone,<br/>ChatGPT, any app"] -->|"https + passphrase"| S2["NextDNS-Agent-MCP"]
    end
    S1 --> N["NextDNS"]
    S2 --> N
```

Menus in these apps change often. If a label below doesn't match what you see, look for "MCP", "Connectors" or "Tools" in the app's settings.

| App | Same computer | Over the internet |
|---|---|---|
| [Claude Code](#claude-code) | Yes | Yes |
| [Claude Desktop](#claude-desktop) | Yes, or the [extension](claude-desktop-extension.md) | Yes, via claude.ai |
| [Claude website and phone app](#claude-website-and-phone-app) | No | Yes |
| [ChatGPT](#chatgpt) | No | Yes |
| [Codex](#codex) | Yes | Yes |
| [Cursor](#cursor) | Yes | Yes |
| [VS Code (Copilot)](#vs-code) | Yes | Yes |
| [Gemini CLI](#gemini-cli) | Yes | Yes |
| [OpenClaw](#openclaw) | Yes | Yes |
| [Hermes Agent](#hermes-agent) | Yes | Yes |
| [Goose](#goose) | Yes | Yes |
| [Cline](#cline) | Yes | Yes |
| [Roo Code](#roo-code) | Yes | Yes |
| [Continue](#continue) | Yes | Yes |
| [Windsurf (Devin Desktop)](#windsurf-devin-desktop) | Yes | Yes |
| [Zed](#zed) | Yes | Yes |
| [LM Studio](#lm-studio) | Yes | Yes |
| [OpenCode](#opencode) | Yes | Yes |
| [Kiro](#kiro) | Yes | Yes |
| [GitHub Copilot CLI](#github-copilot-cli) | Yes | Yes |
| [Amp](#amp) | Yes | Yes |
| [Warp](#warp) | Yes | Yes |
| [JetBrains AI Assistant](#jetbrains-ai-assistant) | Yes | Yes |
| [Qwen Code](#qwen-code) | Yes | Yes |
| [Crush](#crush) | Yes | Yes |
| [Augment Code](#augment-code) | Yes | Yes |
| [Any other MCP app](#any-other-mcp-app) | Usually | If it supports MCP login (OAuth) |

**What we tested:** both ways end to end with the official MCP Python client against a real NextDNS account (the login page, tokens, listing the tools and calling them), and the Claude Desktop extension installed in Claude Desktop. The app-by-app settings below follow each app's own documentation as of October 2026, linked under each app; tell us in an [issue](https://github.com/s17sh70x2jfl031ag/NextDNS-Agent-MCP/issues/new?template=question.yml) if one has changed.

## Before you start: the command path

Desktop apps sometimes can't find commands that your terminal finds. Get the full path once:

- Mac and Linux: `which nextdns-agent-mcp` (usually `/Users/you/.local/bin/nextdns-agent-mcp`)
- Windows: `where nextdns-agent-mcp`

Use that full path wherever you see `/full/path/to/nextdns-agent-mcp` below.

## Claude Code

Same computer:

```bash
claude mcp add nextdns -s user -- nextdns-agent-mcp stdio
```

Over the internet:

```bash
claude mcp add nextdns -s user --transport http https://your-address/mcp
```

Then run `/mcp` inside Claude Code, choose `nextdns` and log in.

## Claude Desktop

The easiest way is the [Claude Desktop extension](claude-desktop-extension.md): open one file, paste your API key, done.

Already installed the command ([computer setup](setup-computer.md))? Settings → Developer → **Edit Config** opens `claude_desktop_config.json`. Add:

```json
{
  "mcpServers": {
    "nextdns": {
      "command": "/full/path/to/nextdns-agent-mcp",
      "args": ["stdio"]
    }
  }
}
```

Save, then quit and reopen Claude Desktop. To use the internet version instead, add it on the Claude website (below): connectors you add there also show up in Claude Desktop.

## Claude website and phone app

You add the connector on the website, and the phone app picks it up.

1. On [claude.ai](https://claude.ai), open **Settings → Connectors**.
2. Click **Add custom connector**. Name: `NextDNS`. URL: `https://your-address/mcp`.
3. Click **Connect**. The login page opens: tick the profiles Claude may use, choose whether it may change settings, type your passphrase and click **Allow access**.
4. In a chat, turn the connector on from the tools menu.
5. Open the Claude phone app: the connector is already there.

> [!TIP]
> In the connector's settings you can set tools to **Always ask**. Deleting and overwriting already ask twice on their own, but you can make any change wait for your tap.

## ChatGPT

ChatGPT connects over the internet, through **developer mode**. Which plans can use it, and whether it allows changes (write actions), changes over time: check [OpenAI's developer mode page](https://help.openai.com/en/articles/12584461) for your plan.

1. **Settings → Apps & Connectors → Advanced settings →** turn on **Developer mode**.
2. **Create** a connector. URL: `https://your-address/mcp`. Authentication: **OAuth**.
3. Save, then tick the profiles and type your passphrase on the login page that opens.

## Codex

Same computer:

```bash
codex mcp add nextdns -- nextdns-agent-mcp stdio
```

Over the internet:

```bash
codex mcp add nextdns --url https://your-address/mcp
```

```bash
codex mcp login nextdns
```

Both write to `~/.codex/config.toml`, which you can also edit by hand:

```toml
[mcp_servers.nextdns]
command = "nextdns-agent-mcp"
args = ["stdio"]
```

## Cursor

In `~/.cursor/mcp.json` (or Settings → MCP → Add):

```json
{
  "mcpServers": {
    "nextdns": { "command": "/full/path/to/nextdns-agent-mcp", "args": ["stdio"] }
  }
}
```

Over the internet, use `"nextdns": { "url": "https://your-address/mcp" }` instead.

## VS Code

Run **MCP: Add Server** from the command palette, or put this in `.vscode/mcp.json`:

```json
{
  "servers": {
    "nextdns": { "type": "stdio", "command": "/full/path/to/nextdns-agent-mcp", "args": ["stdio"] }
  }
}
```

Over the internet, use `"nextdns": { "type": "http", "url": "https://your-address/mcp" }`.

## Gemini CLI

In `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "nextdns": { "command": "nextdns-agent-mcp", "args": ["stdio"] }
  }
}
```

Over the internet, use `"nextdns": { "httpUrl": "https://your-address/mcp" }`.

## OpenClaw

In `~/.openclaw/openclaw.json` (or Settings → MCP in the OpenClaw app, or `openclaw mcp add`):

```json5
{
  mcp: {
    servers: {
      nextdns: { command: "/full/path/to/nextdns-agent-mcp", args: ["stdio"] }
    }
  }
}
```

Over the internet, use `nextdns: { url: "https://your-address/mcp", transport: "streamable-http", auth: "oauth" }`, then run `openclaw mcp login nextdns` and type your passphrase in the browser. If you use OpenClaw's **Sign in** button instead, the login returns to your OpenClaw address, so add that address to `ALLOWED_REDIRECT_HOSTS` ([below](#if-the-login-page-refuses-your-app)).

> [!WARNING]
> OpenClaw runs tools without asking, by default. To be asked before each change, run `openclaw mcp configure nextdns --approval prompt`.

## Hermes Agent

In `~/.hermes/config.yaml` (or with `hermes mcp add`):

```yaml
mcp_servers:
  nextdns:
    command: "/full/path/to/nextdns-agent-mcp"
    args: ["stdio"]
```

Over the internet:

```yaml
mcp_servers:
  nextdns:
    url: "https://your-address/mcp"
    auth: oauth
```

Run `/reload-mcp` in Hermes (or restart it). It opens the login page in your browser. To log in again later: `hermes mcp login nextdns`.

## Goose

In `~/.config/goose/config.yaml`, or with `goose configure` → Add Extension:

```yaml
extensions:
  nextdns:
    name: nextdns
    cmd: nextdns-agent-mcp
    args: [stdio]
    enabled: true
    type: stdio
    timeout: 300
```

Over the internet, use `type: streamable_http` and `uri: https://your-address/mcp` (the key is `uri`, not `url`) instead of `cmd` and `args`. Goose signs in with OAuth by itself. ([Goose docs](https://goose-docs.ai/docs/getting-started/using-extensions))

## Cline

MCP Servers icon → Configure → **Configure MCP Servers** opens `cline_mcp_settings.json`:

```json
{ "mcpServers": { "nextdns": { "command": "nextdns-agent-mcp", "args": ["stdio"], "disabled": false, "autoApprove": [] } } }
```

Over the internet: `"nextdns": { "type": "streamableHttp", "url": "https://your-address/mcp" }`. Set `type` to `streamableHttp`: left out, Cline uses the older SSE. In the Cline CLI, `cline mcp` has "Run or rerun browser authorization" for the login. ([Cline docs](https://docs.cline.bot/mcp/configuring-mcp-servers))

## Roo Code

**Edit Global MCP** (or **Edit Project MCP** for `.roo/mcp.json`):

```json
{ "mcpServers": { "nextdns": { "command": "nextdns-agent-mcp", "args": ["stdio"], "disabled": false, "alwaysAllow": [] } } }
```

Over the internet: `"nextdns": { "type": "streamable-http", "url": "https://your-address/mcp" }`. ([Roo Code docs](https://roocodeinc.github.io/Roo-Code/features/mcp/using-mcp-in-roo))

## Continue

Add a file in `.continue/mcpServers/`, for example `nextdns.yaml` (MCP works in Agent mode):

```yaml
name: nextdns
version: 0.0.1
schema: v1
mcpServers:
  - name: nextdns
    type: stdio
    command: nextdns-agent-mcp
    args:
      - stdio
```

Over the internet: `type: streamable-http` and `url: https://your-address/mcp` instead of `command` and `args`. ([Continue docs](https://docs.continue.dev/customize/deep-dives/mcp))

## Windsurf (Devin Desktop)

Cascade panel `...` → **Open MCP config file**:

```json
{ "mcpServers": { "nextdns": { "command": "nextdns-agent-mcp", "args": ["stdio"] } } }
```

Over the internet: `"nextdns": { "serverUrl": "https://your-address/mcp" }`. OAuth login is supported. ([Windsurf docs](https://docs.devin.ai/desktop/cascade/mcp))

## Zed

Settings → AI → MCP Servers → **Add Server**, or in `settings.json`:

```json
"context_servers": { "nextdns": { "command": "nextdns-agent-mcp", "args": ["stdio"], "env": {} } }
```

Over the internet: `"nextdns": { "url": "https://your-address/mcp" }`. Zed asks you to log in through MCP's OAuth. By default Zed asks before each tool call (`agent.tool_permissions`). ([Zed docs](https://zed.dev/docs/ai/mcp))

## LM Studio

Program tab → Install → **Edit mcp.json** (LM Studio 0.3.17 or newer). It uses the same format as Cursor:

```json
{ "mcpServers": { "nextdns": { "command": "nextdns-agent-mcp", "args": ["stdio"] } } }
```

Over the internet: `"nextdns": { "url": "https://your-address/mcp" }`. ([LM Studio docs](https://lmstudio.ai/docs/app/mcp))

## OpenCode

In `opencode.json`:

```json
{ "$schema": "https://opencode.ai/config.json", "mcp": { "nextdns": { "type": "local", "command": ["nextdns-agent-mcp", "stdio"], "enabled": true } } }
```

Over the internet: `"nextdns": { "type": "remote", "url": "https://your-address/mcp", "enabled": true }`. The login starts by itself, or run `opencode mcp auth nextdns`. ([OpenCode docs](https://opencode.ai/docs/mcp-servers/))

## Kiro

In `~/.kiro/settings/mcp.json` (or `.kiro/settings/mcp.json` in a project):

```json
{ "mcpServers": { "nextdns": { "command": "nextdns-agent-mcp", "args": ["stdio"], "disabled": false, "autoApprove": [] } } }
```

Over the internet: `"nextdns": { "url": "https://your-address/mcp" }`. The browser login starts by itself when Kiro connects. ([Kiro docs](https://kiro.dev/docs/mcp/configuration/))

## GitHub Copilot CLI

```bash
copilot mcp add nextdns -- nextdns-agent-mcp stdio
```

Over the internet:

```bash
copilot mcp add --transport http nextdns https://your-address/mcp
```

Both write to `~/.copilot/mcp-config.json`. ([GitHub docs](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers))

## Amp

```bash
amp mcp add nextdns -- nextdns-agent-mcp stdio
```

Over the internet:

```bash
amp mcp add nextdns https://your-address/mcp
```

Opening Amp then starts the browser login by itself. The settings live under `amp.mcpServers` in `~/.config/amp/settings.json`. ([Amp docs](https://ampcode.com/docs/customize/mcp))

## Warp

Settings → Agents → MCP servers → **+ Add**:

```json
{ "nextdns": { "command": "nextdns-agent-mcp", "args": ["stdio"] } }
```

Over the internet: `{ "nextdns": { "url": "https://your-address/mcp" } }`. Starting it opens the browser login. ([Warp docs](https://docs.warp.dev/knowledge-and-collaboration/mcp))

## JetBrains AI Assistant

Settings → Tools → AI Assistant → Model Context Protocol (MCP) → **Add**:

```json
{ "mcpServers": { "nextdns": { "command": "nextdns-agent-mcp", "args": ["stdio"] } } }
```

Over the internet: `"nextdns": { "url": "https://your-address/mcp" }`. ([JetBrains docs](https://www.jetbrains.com/help/ai-assistant/mcp.html))

## Qwen Code

```bash
qwen mcp add nextdns nextdns-agent-mcp stdio
```

Over the internet:

```bash
qwen mcp add --transport http nextdns https://your-address/mcp
```

In `~/.qwen/settings.json` the internet key is `httpUrl` (`url` means the older SSE). Manage the login in the `/mcp` dialog. ([Qwen Code docs](https://qwenlm.github.io/qwen-code-docs/en/users/features/mcp/))

## Crush

In `~/.config/crush/crushrc`:

```bash
mcp add nextdns --command nextdns-agent-mcp --args stdio
```

Over the internet:

```bash
mcp add nextdns --type http --url https://your-address/mcp --oauth true
```

Crush asks before every tool call by default. ([Crush docs](https://github.com/charmbracelet/crush/blob/main/docs/config/README.md))

## Augment Code

Augment panel menu → Settings → MCP → **+** (or **Import from JSON**):

```json
{ "mcpServers": { "nextdns": { "command": "nextdns-agent-mcp", "args": ["stdio"] } } }
```

Over the internet (**+ Add remote MCP**): `"nextdns": { "type": "http", "url": "https://your-address/mcp" }`. ([Augment docs](https://docs.augmentcode.com/setup-augment/mcp))

## Any other MCP app

- **On the same computer:** the command is `nextdns-agent-mcp` with the argument `stdio`. Settings come from `~/.config/nextdns-agent-mcp/.env` or environment variables ([settings.md](settings.md)), so you can also pass `NEXTDNS_API_KEY` in the app's `env` block.
- **Over the internet:** the address is `https://your-address/mcp` (Streamable HTTP), with MCP's standard OAuth login: the app registers itself, then opens the login page.

Without installing anything, `uvx` can run it straight from GitHub:

```json
{ "command": "uvx", "args": ["--from", "git+https://github.com/s17sh70x2jfl031ag/NextDNS-Agent-MCP", "nextdns-agent-mcp", "stdio"],
  "env": { "NEXTDNS_API_KEY": "your-key" } }
```

## Is it working?

Ask your AI: *"Use the NextDNS profiles tool."* It should list your profiles and what it may do with each. If not, see [troubleshooting.md](troubleshooting.md).

## Give it a name in the change log

On the same computer, every app shows as "AI app" in the change log. To tell them apart, set `NEXTDNS_APP_NAME` in the app's `env` block (for example `"Claude Code"`). Over the internet, the app's own name is used.

## If the login page refuses your app

Only apps from a list of known addresses may receive the login: Claude, ChatGPT, OpenAI and VS Code on the web, plus any app on your own computer (localhost), which covers most desktop and command-line apps above. If another app shows "Redirect not allowed", add its domain to `ALLOWED_REDIRECT_HOSTS` ([settings.md](settings.md)).
