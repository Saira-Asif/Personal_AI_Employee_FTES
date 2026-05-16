---
name: whatsapp-handler
description: Monitor and respond to WhatsApp messages using Playwright browser automation. Detects urgent keywords, drafts replies, and manages message workflows via browser-mcp.
---

# WhatsApp Handler: Browser Integration

Monitor and respond to WhatsApp messages via WhatsApp Web and Playwright.

## When to Use
- **Message Monitoring**: Triggered by `scheduler-trigger` to check for new messages.
- **Urgent Notifications**: When a contact sends keywords like "urgent", "help", "asap", or "invoice".
- **Communication Request**: When the user asks to "send whatsapp message to...".

## Workflow: Checking Messages

1. **Navigate**: Go to `https://web.whatsapp.com` using `browser-mcp`.
2. **Scan**: Look for unread message indicators (`[aria-label*="unread"]`).
3. **Keyword Detection**: Check the text for keywords defined in `Company_Handbook.md`.
4. **Action**: For urgent or keyword-matching messages, create `Needs_Action/WHATSAPP_<contact>.md`.

## Workflow: Responding

1. **Focus Chat**: Select the target contact in the chat list.
2. **Draft**: Consult `Company_Handbook.md` for response tone.
3. **Approve**: Use `hitl-manager` to save to `Pending_Approval/`.
4. **Send**: ONLY after manual approval, use `browser-mcp` to type and send the message.

## Browser-MCP Quick Reference (WhatsApp)

```bash
# Snapshot to find unread indicators
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_snapshot -p '{}'

# Click on unread chat (use ref from snapshot)
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_click \
  -p '{"element": "Unread chat", "ref": "e12"}'

# Type and send message (ONLY after approval)
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_type \
  -p '{"element": "Message input", "ref": "e45", "text": "...", "submit": true}'
```

## Rules
- **No Unapproved Sends**: Every message send requires a matching file in `Approved/`.
- **Keyword Filtering**: Only escalate messages matching the keyword list.
- **Privacy First**: Never capture or store sensitive message data outside the vault.
- **Human-Like Delay**: Use `browser_wait_for` to mimic human typing/reading delays.
