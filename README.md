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

Build both packages with Python 3.11 or later:

```bash
python3 .openai-plugin/build.py
```

This creates two archives under `.openai-plugin/dist/`:

- `attention-claude-<version>.zip` preserves the Claude layout, HTTP connection, skill, license and README.
- `attention-openai-<version>.zip` contains root `plugin.json`, `mcp.json`, the same skill and license, and the OpenAI icon.

The OpenAI connection declares OAuth Dynamic Client Registration (DCR) and the existing `mcp:read` and `mcp:write` scopes. Authentication endpoints come from production discovery. No credentials or fixed tokens are packaged. Unchanged source files produce byte-identical archives.

### Package validation

Install Python 3.11+, Node.js 22 and the pinned validators:

```bash
python3 -m venv .openai-plugin/.venv
source .openai-plugin/.venv/bin/activate
python3 -m pip install -r .openai-plugin/requirements.txt
npm install --global @anthropic-ai/claude-code@2.1.273
python3 -m unittest discover -s .openai-plugin -p 'test_*.py'
python3 .openai-plugin/validate.py .openai-plugin/dist/attention-claude-1.1.1.zip .openai-plugin/dist/attention-openai-1.1.1.zip
```

The regression command builds the deliverable archives and compares them with one second build in a temporary directory. The validator inspects the actual ZIPs, validates portable JSON using pinned local schemas, checks OpenAI OAuth and listing fields, inspects the icon, and runs `claude plugin validate --strict` on the extracted Claude package. These checks make no OAuth or MCP requests. CI uses the same commands and uploads the two ZIPs with its validation report.

The portable MCP schema does not describe OpenAI server extensions. Validation retains the upstream schema and adds the documented OAuth declaration to its in-memory validation schema. See `.openai-plugin/schemas/README.md` for source URLs and checksums.

### Submission preparation remains incomplete

Package validation is separate from public-submission readiness. Add `--submission` to the validation command to fail when required package review fields are missing.

The listing uses the published MCP overview, privacy policy and terms URLs, verified on November 11, 2026. The publisher must confirm that its privacy policy and terms cover the submitted integration. These items still need completion:

- A verified HTTPS support page with a working support contact.
- Exactly five positive and three negative reviewer cases with the final demo data, expected tools and results; run them with the reviewer account. The manifest's optional review prompts are not those cases.
- An accessible recording of the actual submitted functionality.
- Verified publisher identity, country availability and any applicable commerce declaration.
- Reviewer credentials in the portal's private fields, plus domain verification, a current tool scan and policy attestations.

Do not put reviewer credentials in either archive. No country restriction or commerce behavior is declared without publisher confirmation.

For host acceptance, extract the Claude archive and load it with `claude --plugin-dir <extracted-directory>`. Confirm `attention:conversations` is discoverable, then complete OAuth and run a read-only search with a permitted sample account. Load the OpenAI archive in the intended ChatGPT/Codex host and repeat skill discovery and the same read-only scenario. Archive validation does not prove these authenticated host checks or OpenAI approval.

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
