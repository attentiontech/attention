# Attention Plugin

Plugin for Claude Code, Grok Build, ChatGPT, and Codex that connects your assistant to [Attention](https://www.attention.com) — an AI-powered conversational intelligence platform that records calls, transcribes, and analyzes sales conversations.

## What's Included

This plugin provides:

- **MCP Server Connection** — Connects to Attention's remote MCP server at `https://api.attention.tech/mcp` with OAuth 2.0 authentication
- **Skills** — Agent skills for searching conversations and getting AI-powered insights

The OpenAI package reuses `.claude-plugin/plugin.json`, `.mcp.json`, and `skills/`. OpenAI-specific metadata, the icon, and the packaging script live in `.openai-plugin/`.

## Installation

### Claude Code: official marketplace

```
/plugin install attention
```

### Claude Code: local testing

```bash
claude --plugin-dir ./path/to/attention
```

Then authenticate:

```
/mcp
```

Select "attention" and complete the OAuth flow in your browser.

### Grok Build

In Grok Build, open `/plugin`, search for **Attention**, and install. On first connect, sign in with your Attention account to complete the OAuth flow in your browser.

Grok Build reads the same plugin files as Claude Code (`.claude-plugin/plugin.json`, `.mcp.json`, `skills/`), so there's nothing extra to configure.

### ChatGPT and Codex

Build the package with Python 3.9 or later:

```bash
python3 .openai-plugin/build.py
```

This creates `.openai-plugin/dist/attention-openai-<version>.zip` with the shared metadata, MCP connection, skills, and license. The script adds the OpenAI metadata and icon and translates the HTTP transport name to `streamable-http`. Use the generated ZIP for [OpenAI's supported package layout](https://developers.openai.com/plugins/build/plugins); `.openai-plugin/` is the source folder.

## Available MCP Tools

Tools are discovered dynamically from the server at connection time. Run `/mcp` in Claude Code to see all available tools, or check the [Attention MCP Server Docs](https://docs.attention.com/mcp/overview) for the full reference.

## Plugin Structure

```
attention/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest (name, version, metadata)
├── .mcp.json                # MCP server configuration (remote HTTP)
├── .openai-plugin/
│   ├── manifest-overlay.json # OpenAI presentation metadata
│   ├── assets/
│   │   └── attention-icon.png
│   └── build.py              # Packages the shared sources for OpenAI
├── skills/
│   └── conversations/
│       └── SKILL.md         # Shared conversation skill
└── README.md
```

## Testing

1. **Local testing with `--plugin-dir`**:
   ```bash
   claude --plugin-dir ./attention
   ```

2. **Verify plugin loaded**:
   ```
   /help
   ```
   You should see `attention:conversations` in the skills list.

3. **Authenticate**:
   ```
   /mcp
   ```
   Select "attention" and complete OAuth in your browser.

4. **Test tools**:
   ```
   Search for conversations from last week
   ```

5. **Validate plugin structure**:
   ```bash
   claude plugin validate ./attention
   ```

## Server Details

| Property | Value |
|----------|-------|
| Server URL | `https://api.attention.tech/mcp` |
| Transport | Streamable HTTP (stateless) |
| Authentication | OAuth 2.0 with PKCE |
| Scopes | `mcp:read`, `mcp:write` |
| OAuth Discovery | `https://api.attention.tech/.well-known/oauth-authorization-server` |

The plugin only talks to `api.attention.tech`. It needs no API key and reads no local files or environment variables: you sign in with your Attention account and the agent acts as that account (scopes `mcp:read`, `mcp:write`).

## Documentation

- [Attention MCP Server Docs](https://docs.attention.com/mcp/overview)
- [Claude Code Plugins Docs](https://code.claude.com/docs/en/plugins)
- [xAI Plugin Marketplace](https://github.com/xai-org/plugin-marketplace)
- [MCP Specification](https://modelcontextprotocol.io/)
