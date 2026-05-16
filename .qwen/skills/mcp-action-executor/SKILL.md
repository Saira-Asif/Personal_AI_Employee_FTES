---
name: mcp-action-executor
description: General-purpose executor for Model Context Protocol (MCP) actions. Handles server lifecycle, parameter validation, and error recovery for all available MCP servers.
---

# MCP Action Executor: The Hands

Execute any external action through configured MCP servers with full auditing.

## When to Use
- **Execution Request**: When `vault-processor` or `hitl-manager` identifies an approved action.
- **System Maintenance**: To start or stop MCP servers.
- **Diagnostic Check**: To verify MCP server availability.

## Supported Servers & Actions

| Server | Primary Actions |
|--------|----------------|
| **filesystem** | Read, write, list, move files |
| **gmail** | List, get, create_draft, send_email |
| **browser** (Playwright) | Navigate, snapshot, click, type, evaluate |
| **whatsapp** | Send message, list chats (via browser) |
| **calendar** | Create event, list events |
| **linkedin** | Post content, list notifications (via browser) |

## Workflow: Executing an Action

1. **Verify**: Check `Approved/` for the authorization record.
2. **Parameters**: Extract the correct parameters from the request file.
3. **Execute**: Call the appropriate MCP tool using `scripts/mcp-client.py`.
4. **Log**: Store the raw response and status in the audit log.
5. **Recover**: If the server is down, try `bash scripts/start-server.sh`.

## MCP Client Quick Reference

```bash
# General mcp-client.py syntax
python3 scripts/mcp-client.py call -u <server_url> -t <tool_name> -p '<json_params>'
```

## Rules
- **No Direct Execution**: Always verify a matching approval record for sensitive actions.
- **Atomic Results**: Every MCP call MUST return a clear success or failure result.
- **Dry-Run Mode**: Use `dry_run: true` in the parameters for testing new or complex steps.
- **Secrets Management**: Never include API keys or passwords in the vault; use environment variables.
