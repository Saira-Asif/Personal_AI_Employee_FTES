---
name: mcp-action-executor
description: Execute external actions via MCP servers including email sending, browser automation, calendar management, and social media posting. Handles HITL approval gates for all sensitive actions.
---

# MCP Action Executor Skill

## Overview
This skill enables the AI Employee to execute external actions through Model Context Protocol (MCP) servers. It is the "hands" of the system - connecting to Gmail, browsers, calendars, messaging platforms, and payment portals.

**Silver Tier Focus**: This skill bridges the gap between the local vault and the outside world.

## When to Use
- When an approved action file in `Pending_Approval/` requires external execution
- When the orchestrator triggers an approved task
- When processing items that need API calls (send email, post message, create calendar event)
- When interacting with websites via browser automation (payments, form submissions)

## Available MCP Servers

| Server | Capabilities | Approval Required |
|--------|-------------|-------------------|
| filesystem | Read, write, list files | No (vault operations) |
| email-mcp | Send, draft, search emails | Yes (all sends) |
| browser-mcp | Navigate, click, fill forms | Yes (all interactions) |
| calendar-mcp | Create, update, list events | No (read), Yes (create/update) |
| whatsapp-mcp | Send messages, read chats | Yes (all sends) |
| payment-mcp | Initiate payments, check balances | Yes (always) |
| social-mcp | Post to Facebook, Instagram, Twitter | Yes (all posts) |

## Workflow

### 1. Check for Approved Actions
```
1. Scan Pending_Approval/ for approved files
2. Verify approval status is confirmed
3. Parse action type and parameters
4. Execute via appropriate MCP server
5. Log result to Done/ with timestamp and outcome
6. Remove or archive the approval file
7. Update Dashboard.md
```

### 2. Execute by Action Type

#### Email Send
```yaml
Action: send_email
MCP: email-mcp
Parameters:
  to: recipient@email.com
  cc: cc@email.com (optional)
  subject: "Subject line"
  body: "Email body text"
  attachments: ["/path/to/file.pdf"] (optional)
```

#### Browser Automation
```yaml
Action: browser_automate
MCP: browser-mcp
Parameters:
  url: https://example.com
  steps:
    - click: "#login-button"
    - fill: "#email-input", value: "user@email.com"
    - fill: "#password-input", value: "${BANK_PASSWORD}"
    - click: "#submit-button"
  dry_run: true
  screenshot: true
```

#### Calendar Event
```yaml
Action: create_calendar_event
MCP: calendar-mcp
Parameters:
  title: "Client meeting - Project Alpha"
  start: "2026-04-20T10:00:00"
  end: "2026-04-20T11:00:00"
  attendees: ["client@email.com"]
  description: "Quarterly review meeting"
  reminder_minutes: 30
```

#### WhatsApp Message
```yaml
Action: send_whatsapp
MCP: whatsapp-mcp
Parameters:
  contact: "Client Name"
  message: "Hi, your invoice has been processed."
  is_urgent: false
```

#### Payment Initiation
```yaml
Action: initiate_payment
MCP: payment-mcp
Parameters:
  payee: "Client A"
  amount: 500.00
  currency: USD
  reference: "Invoice #1234"
  bank_account: "XXXX1234"
```

#### Social Media Post
```yaml
Action: post_to_social
MCP: social-mcp
Parameters:
  platform: "facebook"
  content: "Post text here"
  media: ["/path/to/image.jpg"] (optional)
  schedule_time: "2026-04-20T09:00:00" (optional)
  platforms: ["facebook", "instagram", "twitter"] (multi-post)
```

### 3. Approval Gate Enforcement

**CRITICAL RULE**: Never execute sensitive actions without confirmed approval.

| Action Category | Auto-Execute Threshold | Always Require Approval |
|-----------------|----------------------|----------------------|
| Email replies | To known contacts only | New contacts, bulk sends |
| Calendar events | Read-only | Create, update, delete |
| Payments | Never | All payments, no exceptions |
| WhatsApp sends | Reply to direct message | New contacts, broadcasts |
| Social posts | Scheduled posts only | Replies, DMs, unscheduled |
| Browser actions | Read-only navigation | Any form submission, payment |

### 4. Dry Run Support
All MCP actions support `--dry-run` mode:
```yaml
dry_run: true
```
In dry-run mode:
- Log the intended action
- Do not execute the actual MCP call
- Show the user what would happen
- Useful for testing and debugging

### 5. Error Handling and Retry
```
1. If MCP call fails:
   - Log the error to Done/ with error details
   - Create a new action file in Needs_Action/ for retry
   - Alert the user if the action was time-sensitive
   - Never retry payments automatically (always require fresh approval)
   - Retry transient errors (timeout, rate limit) up to 3 times with exponential backoff
```

### 6. Audit Logging
Every MCP action must be logged:
```markdown
---
type: audit_log
timestamp: <YYYY-MM-DDTHH:MM:SS>
action_type: <email_send/browser_automate/payment_initiate>
actor: <qwen_code_agent>
target: <recipient@email.com or URL>
parameters: <key params used>
approval_status: <approved/auto>
approved_by: <human or "auto">
result: <success/error/timeout>
---

# MCP Action Audit Log

## Action Details
- **Type**: Email Send
- **Target**: client@email.com
- **Subject**: January 2026 Invoice
- **Approved By**: Human (moved from Pending_Approval/)
- **Result**: Success (delivered at 10:32 AM)

## MCP Response
<Raw response from MCP server>
```

## Rules
1. NEVER execute payments, emails, or messages without confirmed HITL approval
2. ALWAYS use dry_run first for any new/unknown MCP action
3. Log every action to audit logs with full details
4. If MCP server is unavailable, queue the action locally and retry when restored
5. Rate limit: max 10 emails/hour, max 3 payments/day, max 5 social posts/hour
6. Sensitive data (passwords, tokens) must come from environment variables, never from vault files
7. For browser automation, always take screenshots before and after key steps
8. Degrade gracefully: if Gmail is down, queue emails locally; if banking API times out, never auto-retry payments
