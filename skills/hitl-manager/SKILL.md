---
name: hitl-manager
description: Human-in-the-Loop approval management. Handles approval request creation, notification, escalation for stale approvals, auto-approval for safe recurring actions, and approval history tracking.
---

# HITL Manager Skill

## Overview
This skill manages the Human-in-the-Loop (HITL) approval workflow. It creates approval requests, notifies the user, escalates stale approvals, auto-approves safe recurring actions, and maintains an approval history for auditing.

## When to Use
- When any action requires human approval before execution
- When processing items in `Pending_Approval/`
- When reviewing stale or expired approval requests
- When a previously-approved action has been rejected
- When analyzing approval patterns for auto-approval opportunities

## Approval Request Lifecycle

```
Needs_Action → Create Approval Request → Pending_Approval/ → User Reviews
     ↑                                          ↓
     ← Approved ← Move to approved folder    Rejected → Move to rejected folder
            ↓                                         ↓
     Execute via MCP                           Log rejection, notify user
            ↓
     Move to Done/
```

## Workflow

### 1. Create Approval Request
When an action requires approval:
1. Create file in `Pending_Approval/` with standard naming:
   `<ACTION_TYPE>_<description>_<YYYY-MM-DD_HHMM>.md`
2. Include all relevant details (see template below)
3. Set expiry timestamp (default: 24 hours)
4. Log the request creation to `Tasks/approval_history.md`

### 2. Approval Request Template
```markdown
---
type: approval_request
action_type: <email_send/payment_initiate/whatsapp_send/post_to_social/browser_action>
created: <YYYY-MM-DDTHH:MM:SS>
expires: <YYYY-MM-DDTHH:MM:SS>
status: pending
priority: <CRITICAL/HIGH/MEDIUM/LOW>
source_action: <original Needs_Action file name>
---

# Approval Request: <Action Description>

## Action Details
- **Type**: <What will be done>
- **Target**: <Who/what will be affected>
- **Amount**: $<amount> (if payment)
- **Urgency**: <Why this needs to be done now>

## Context
<Background information, why this action is needed>

## Proposed Action
<Exactly what will happen if approved>

## Risk Assessment
- **Low Risk**: Routine, previously-approved action
- **Medium Risk**: New payee, unusual amount, first time
- **High Risk**: Large amount, new contact, irreversible action

## To Approve
Move this file to the approved folder.

## To Reject
Move this file to the rejected folder with a reason.

## Auto-Approval Eligibility
<Yes/No — is this eligible for auto-approval?>
```

### 3. Notification
When an approval request is created:
1. Update Dashboard.md with pending count
2. Include in next daily briefing
3. If CRITICAL priority: create alert in `Inbox/ALERT_<description>.md`

### 4. Process Approved Actions
When a file appears in the approved folder:
1. Verify the approval is still valid (not expired)
2. Read the action details
3. Execute via mcp-action-executor skill
4. Log to `Done/` with approval metadata
5. Update `Tasks/approval_history.md`:
```markdown
## Approved: <Action>
- **Approved At**: <timestamp>
- **Approved By**: <human>
- **Executed At**: <timestamp>
- **Result**: <success/error>
- **Original Request**: <link to file>
```

### 5. Process Rejected Actions
When a file appears in the rejected folder:
1. Read the rejection reason (if provided)
2. Log to `Tasks/approval_history.md`
3. Notify the original requester (if applicable)
4. Do not attempt to re-execute

### 6. Escalate Stale Approvals
Check `Pending_Approval/` for expired or stale items:
```
1. Scan all files in Pending_Approval/
2. If file has expired (past expiry timestamp):
   - Update status to "expired"
   - Create alert in Inbox/
   - Move to Done/ with "expired" status
3. If file is older than 48 hours (but not expired):
   - Add reminder note
   - Include in daily briefing
4. If file is CRITICAL and older than 4 hours:
   - Create URGENT alert in Inbox/
```

### 7. Auto-Approval Logic
Certain safe, recurring actions can be auto-approved:

| Condition | Auto-Approve? | Example |
|-----------|--------------|---------|
| Same action executed 5+ times with human approval | Yes | Monthly subscription payment to known payee |
| Amount < $50 to known contact | Yes | Regular invoice payment to established client |
| Email reply to known contact, no attachments | Yes | Replying to regular client emails |
| New payee or amount > $100 | No | Always require approval |
| First time action | No | Always require approval |
| Social media post (not scheduled) | No | Always require approval |
| Payment of any amount to new recipient | No | Always require approval |

Auto-approval history is logged to `Tasks/approval_history.md`:
```markdown
## Auto-Approved: <Action>
- **Reason**: Executed 12 times previously, all approved by human
- **Approved At**: <timestamp>
- **Executed At**: <timestamp>
- **Result**: <success/error>
```

### 8. Approval History Analysis
Monthly review of `Tasks/approval_history.md`:
1. Count total approvals, rejections, auto-approvals, expirations
2. Identify patterns for auto-approval candidates
3. Flag frequently-rejected action types
4. Report approval turnaround time (request → approval → execution)
5. Include findings in monthly CEO briefing

## Rules
1. NEVER bypass approval for payments, regardless of amount or frequency
2. ALWAYS log every approval decision with timestamp
3. Escalate CRITICAL items that sit unapproved for 4+ hours
4. Expired approvals should not be executed — create a new request if still needed
5. Auto-approval is opt-in: the system suggests, human confirms the rule
6. Approval history is append-only — never delete entries
7. If an approval file is moved outside Pending_Approval/ without approval/rejection, log it as "cancelled"
