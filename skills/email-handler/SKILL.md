---
name: email-handler
description: Process Gmail inputs, draft replies, and manage email workflows via MCP servers or scripts. Handles detection of important emails, creates action files, drafts replies, and manages approval before sending.
---

# Email Handler Skill

## Overview
This skill enables the AI Employee to monitor Gmail inputs, classify incoming emails, draft intelligent replies, and manage the complete email workflow. It integrates with Gmail for reading and sending emails.

## When to Use
- When Gmail Watcher detects new emails in Inbox
- When the user asks to check or respond to email
- When processing email-related items in Needs_Action/
- When drafting invoices, follow-ups, or scheduled emails

## Workflow

### 1. Check for New Emails
```
1. Use Gmail API/Watcher to list unread/important emails
2. Filter by priority rules (see below)
3. Create action files in Needs_Action/ for items requiring processing
4. Archive routine emails automatically
```

### 2. Classify and Prioritize
For each new email, determine:

| Priority | Criteria | Action |
|----------|----------|--------|
| CRITICAL | Keywords: invoice, payment, urgent, asap, legal, contract | Create action file immediately, alert user |
| HIGH | From known contacts, client requests, deadlines | Create action file, process within 24h |
| MEDIUM | Newsletters, updates, non-urgent requests | File to appropriate folder, process when available |
| LOW | Promotions, social notifications, marketing | Archive automatically, summarize in briefing |

### 3. Draft Replies
When a reply is needed:

1. Read the full email thread for context
2. Consult Company_Handbook.md for tone and rules
3. Check Business_Goals.md for relevant priorities
4. Draft the reply following these rules:
   - Match the sender's tone (formal/casual)
   - Be specific and actionable
   - Include relevant deadlines or next steps
   - Attach any referenced documents

### 4. Approval Before Sending
For email sends (not drafts):
1. Save draft to `Pending_Approval/EMAIL_<contact>_<date>.md`
2. Include full email content, recipients, and any attachments
3. Wait for user to move file to approved state
4. Send via `scripts/send_email.py` only after approval

### 5. Send Approved Emails
When an approval file is confirmed:
1. Read the approval details
2. Use `scripts/send_email.py` with the correct parameters:
   `python scripts/send_email.py --to <recipient> --subject <subject> --body <body>`
3. Log the sent email to `Done/` with timestamp
4. Update Dashboard.md

## Email Action File Template
```markdown
---
type: email_action
source: gmail_watcher
from: sender@email.com
to: your@email.com
subject: Email Subject Line
date_received: <YYYY-MM-DD>
priority: <CRITICAL/HIGH/MEDIUM/LOW>
status: pending
created: <timestamp>
---

# Email Action Required

## From
<Name> <email@domain.com>

## Subject
<Subject line>

## Summary
<Brief summary of the email content>

## Full Content
<Paste or summarize the email body>

## Required Action
- [ ] Read and understand the request
- [ ] Draft appropriate response
- [ ] Create approval request if sending
- [ ] Execute or wait for approval

## Context
[Any relevant context from Business_Goals.md or previous interactions]

## Suggested Response
<Draft reply here for review>
```

## Email Approval Request Template
```markdown
---
type: approval_request
action: send_email
to: recipient@email.com
cc: cc@email.com
subject: Reply: Original Subject
created: <timestamp>
status: pending
expires: <timestamp + 24h>
---

# Email Approval Request

## Recipients
- **To**: <recipient@email.com>
- **CC**: <cc@email.com>

## Subject
Reply: <Subject>

## Body
<Full email body text>

## Attachments
- <List any attachments>

## To Approve
Move this file to approved folder.

## To Reject
Move this file to rejected folder with reason.
```

## Rules
1. Never send emails without explicit approval (HITL)
2. Always read Company_Handbook.md for communication rules
3. Log every email read/draft/sent to Done/
4. Archive or categorize newsletters automatically
5. Flag any emails containing payment requests, legal terms, or contracts as CRITICAL
6. Use the email action file format for all email-related tasks
7. Check for new emails at least every 30 minutes during business hours
8. Summarize email activity in daily briefing
