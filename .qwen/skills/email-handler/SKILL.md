---
name: email-handler
description: Monitor Gmail, prioritize unread messages, and manage intelligent email responses via Gmail MCP server. Enforces HITL for all outgoing communications.
---

# Email Handler: Gmail Integration

Manage your inbox by triage, drafting, and responding via Gmail MCP.

## When to Use
- **Inbox Triage**: At the start of every session to identify new work.
- **Poll Request**: Triggered by `scheduler-trigger` to check for emails.
- **Email Request**: When the user asks to "send email" or "reply to...".

## Triage Workflow

1. **List**: `gmail_mcp.list_messages(query="is:unread", max_results=10)`
2. **Prioritize**:
   - **CRITICAL**: Invoice, payment, legal, contract, urgent.
   - **HIGH**: Known contacts, client requests, deadlines.
   - **MEDIUM**: General updates, non-urgent inquiries.
   - **LOW**: Newsletters, promotions (archive automatically).
3. **Action**: For HIGH/CRITICAL, create `Needs_Action/EMAIL_<id>.md`.

## Response Workflow

1. **Read**: Get full message content and thread history.
2. **Consult**: Check `Company_Handbook.md` for tone and policies.
3. **Draft**: Create the response in `Active_Project/`.
4. **Approve**: Use `hitl-manager` to save to `Pending_Approval/`.
5. **Send**: Only use `gmail_mcp.send_email` AFTER manual approval in `Approved/`.

## Gmail MCP Quick Reference

```bash
# Get message content
python3 scripts/mcp-client.py call -u http://localhost:8808 -t gmail_get_message \
  -p '{"message_id": "<id>"}'

# Create a draft
python3 scripts/mcp-client.py call -u http://localhost:8808 -t gmail_create_draft \
  -p '{"to": "...", "subject": "...", "body": "..."}'

# Send an email (ONLY after approval)
python3 scripts/mcp-client.py call -u http://localhost:8808 -t gmail_send_email \
  -p '{"to": "...", "subject": "...", "body": "..."}'
```

## Rules
- **No Unapproved Sends**: Every `send_email` call requires a matching file in `Approved/`.
- **Tone Matching**: Match the sender's tone unless `Company_Handbook.md` specifies otherwise.
- **Logging**: Every email read or sent must be logged to `Done/` with timestamp.
