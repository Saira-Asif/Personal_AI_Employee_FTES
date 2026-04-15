# MCP Servers

This directory contains Model Context Protocol (MCP) server configurations for the AI Employee.

## What are MCP Servers?

MCP servers are the "hands" of your AI Employee - they allow Qwen Code to interact with external systems like email, browsers, calendars, and messaging platforms.

## Current Status

No MCP servers are installed in Bronze Tier. This is expected - Bronze Tier focuses on the file-based workflow where:
- Watchers detect new inputs
- Qwen Code reads/writes files in the vault
- Human approves actions via file movement

## Available Servers (Silver Tier+)

| Server | Purpose | Tier |
|--------|---------|------|
| email-mcp | Gmail integration | Silver |
| browser-mcp | Browser automation | Silver |
| calendar-mcp | Calendar management | Silver |
| slack-mcp | Slack integration | Silver |

## Configuration

See `mcp-config.json` for server configuration templates. Each server requires:
1. Installation of the MCP server package
2. API credentials placed in `AI_Employee_Vault/credentials/` (never commit credentials)
3. Configuration in your Qwen Code MCP settings

## Setting Up MCP Servers

1. Install the MCP server package
2. Configure credentials in the vault's `credentials/` folder
3. Update `mcp-config.json` with actual paths
4. Configure Qwen Code to use the MCP server:
   ```json
   // ~/.config/claude-code/mcp.json
   {
     "servers": [
       {
         "name": "email",
         "command": "node",
         "args": ["/path/to/email-mcp/index.js"]
       }
     ]
   }
   ```

## Security Notes

- Never commit credentials to version control
- Keep credentials in `AI_Employee_Vault/credentials/` (gitignored)
- Use environment variables where possible
- Review MCP server permissions before granting access
