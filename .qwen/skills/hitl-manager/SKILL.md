---
name: hitl-manager
description: Manage the Human-in-the-Loop approval gate. Handles creation, monitoring, and execution of approved tasks for sensitive operations like payments, emails, and social posts.
---

# HITL Manager: Human Approval Gate

Enforce safety by requiring human approval for all sensitive actions.

## When to Use
- **Action Request**: When a task requires a sensitive action (email send, payment, social post).
- **Approval Check**: Triggered by `vault-processor` or `scheduler-trigger` to see what is approved.
- **Cleanup**: When an approval file expires or is rejected.

## Workflow: Creating a Request

1. **Format**: Create a file in `Pending_Approval/`.
2. **Standard Template**:
```markdown
---
type: approval_request
action_type: <email_send|payment|whatsapp_send|linkedin_post>
created: <YYYY-MM-DD HH:MM>
expires: <+24h>
status: pending
---

# Approval Request: <Action Description>

## Proposed Action
<Exact parameters for the MCP call>

## Context
<Why this action is being taken>

## To Approve
Move this file to `AI_Employee_Vault/Approved/`.

## To Reject
Move this file to `AI_Employee_Vault/Rejected/`.
```

## Workflow: Executing Approved Tasks

1. **Scan**: Look for files in `Approved/`.
2. **Execute**: Trigger the appropriate MCP skill with the parameters from the file.
3. **Log**: Record the result in `Done/` and `Tasks/approval_history.md`.
4. **Clean**: Archive the approval file to `Done/`.

## Rules
- **No Manual Bypass**: Never execute a sensitive action directly without a matching approval record.
- **Expiration**: Stale approvals (>24h) should be moved to `Rejected/` with status "expired".
- **One-Time Use**: Each approval record corresponds to EXACTLY one execution.
- **Audit Trace**: Always link back to the original `Needs_Action/` file.
