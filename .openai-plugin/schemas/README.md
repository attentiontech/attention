# Pinned Agent Plugins schemas

Unmodified Agent Plugins 1.0.0 schemas downloaded on 2026-11-11:

- https://agent-plugins.org/schemas/1.0.0/plugin.schema.json
  SHA-256: `0a4aad95ce337878ad38802ebf0daa3fde76abe3f65400c86bcbb1ec0b3ab883`
- https://agent-plugins.org/schemas/1.0.0/mcp.schema.json
  SHA-256: `6539175bfcdf43085855183e86da40ea94b166547a72b47ae9a0a390516d3acb`

Validation uses these local copies without retrieving schemas during a build.
The portable MCP schema predates the server-level OpenAI namespace. The validator
adds only the documented `extensions.com.openai.auth` contract to its in-memory
schema; the upstream copies stay unchanged.

OpenAI authentication reference:
https://developers.openai.com/plugins/build/plugins#configure-mcp-authentication
