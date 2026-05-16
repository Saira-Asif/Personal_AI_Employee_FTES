---
name: vault-processor
description: Process items in the AI Employee vault - read from Needs_Action, create plans, execute tasks, manage approvals, and coordinate with MCP actions via Silver tier skills
---

# Vault Processor Skill

## Overview
This skill enables the AI Employee to process items from the Needs_Action folder, create actionable plans, execute tasks, and manage the complete workflow lifecycle. It coordinates with Silver tier skills (email-handler, mcp-action-executor, hitl-manager, scheduler-trigger) for external actions.

## When to Use
- When there are files in the `Needs_Action/` folder requiring processing
- When tasks need to be broken down into actionable steps
- When the dashboard needs updating
- When daily/weekly summaries are required
- When processing email, WhatsApp, or social media action files

## Workflow

### 1. Scan for Work
```
1. Check Needs_Action/ folder for new items
2. Review Pending_Approval/ for user-approved actions
3. Check Inbox/ for any uncategorized items
4. Check Active_Project/ for stalled work
```

### 2. Process Items
For each item in Needs_Action/:
1. Read and understand the content
2. Determine source type (file_drop, gmail_watcher, whatsapp_watcher, scheduled_trigger)
3. Determine priority level (CRITICAL, HIGH, MEDIUM, LOW)
4. Move to Active_Project/ while working
5. Create a Plan.md if multi-step work is needed
6. Execute the work (or delegate to appropriate Silver tier skill)
7. Move to Done/ with completion notes
8. Update Dashboard.md

### 3. Source Type Routing
| Source | Route To |
|--------|----------|
| file_drop | Process directly with this skill |
| gmail_watcher | email-handler skill |
| whatsapp_watcher | mcp-action-executor skill (whatsapp-mcp) |
| scheduled_trigger | scheduler-trigger skill |
| mcp_action | mcp-action-executor skill |

### 4. Create Plans for Complex Tasks
When a task requires multiple steps:
```markdown
---
type: plan
created: <timestamp>
status: in_progress
priority: <level>
---

# Plan: <Task Name>

## Objective
<Brief description of what needs to be achieved>

## Steps
- [ ] Step 1: <Description>
- [ ] Step 2: <Description>
- [ ] Step 3: <Description>

## Notes
<Any relevant context or considerations>

## Completion Criteria
<What does "done" look like?>
```

### 5. Handle Approvals
For sensitive actions, use the hitl-manager skill:
1. Create file in `Pending_Approval/` via hitl-manager template
2. Wait for user to move to approved state
3. Execute via mcp-action-executor only after approval confirmed
4. Log to approval history

### 6. Error Handling
When processing fails:
1. Log the error to `Done/` with error details and timestamp
2. Create a retry item in `Needs_Action/` if the error is transient
3. Alert the user for non-transient errors
4. Move the original file to `Done/` with "failed" status and notes

### 7. Update Dashboard
After each completed task, update Dashboard.md with:
- Task completion count
- Current system status
- Any new items needing attention
- Last briefing timestamp
- Pending approval count

## Output Format

### Task Completion Log
```markdown
---
type: task_log
task: <Task name>
completed: <timestamp>
status: complete
source: <file_drop/gmail_watcher/whatsapp_watcher/scheduled_trigger>
---

# Task Completed: <Task Name>

## Summary
<Brief description of what was done>

## Actions Taken
- Action 1
- Action 2

## Files Created/Modified
- List of files

## MCP Actions (if applicable)
- <MCP server used, action taken, result>

## Next Steps
- Any follow-up items
```

## Rules
1. Always read Company_Handbook.md before processing to understand rules
2. Check Business_Goals.md for context and priorities
3. Never execute sensitive actions without approval (use hitl-manager)
4. Log all work in the appropriate folders
5. Update Dashboard.md after each task
6. Move completed items to Done/ with descriptive completion notes
7. Delegate to appropriate Silver tier skill when source type requires it
8. Handle errors gracefully — log, alert, and retry where appropriate
9. Maintain claim-by-move rule: first agent to move item from Needs_Action/ owns it
10. Never store credentials in vault files — use environment variables
