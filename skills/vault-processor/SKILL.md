---
name: vault-processor
description: Process items in the AI Employee vault - read from Needs_Action, create plans, execute tasks, and move to Done
---

# Vault Processor Skill

## Overview
This skill enables the AI Employee to process items from the Needs_Action folder, create actionable plans, execute tasks, and manage the complete workflow lifecycle.

## When to Use
- When there are files in the `Needs_Action/` folder requiring processing
- When tasks need to be broken down into actionable steps
- When the dashboard needs updating
- When daily/weekly summaries are required

## Workflow

### 1. Scan for Work
```
1. Check Needs_Action/ folder for new items
2. Review Pending_Approval/ for user-approved actions
3. Check Inbox/ for any uncategorized items
```

### 2. Process Items
For each item in Needs_Action/:
1. Read and understand the content
2. Determine priority level (CRITICAL, HIGH, MEDIUM, LOW)
3. Move to Active_Project/ while working
4. Create a Plan.md if multi-step work is needed
5. Execute the work
6. Move to Done/ with completion notes
7. Update Dashboard.md

### 3. Create Plans for Complex Tasks
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

### 4. Handle Approvals
For sensitive actions:
1. Create file in `Pending_Approval/` with details
2. Wait for user to move to approved state
3. Execute only after approval confirmed

### 5. Update Dashboard
After each completed task, update Dashboard.md with:
- Task completion count
- Current status
- Any new items needing attention

## Output Format

### Task Completion Log
```markdown
---
type: task_log
task: <Task name>
completed: <timestamp>
status: complete
---

# Task Completed: <Task Name>

## Summary
<Brief description of what was done>

## Actions Taken
- Action 1
- Action 2

## Files Created/Modified
- List of files

## Next Steps
- Any follow-up items
```

## Rules
1. Always read Company_Handbook.md before processing to understand rules
2. Check Business_Goals.md for context and priorities
3. Never execute sensitive actions without approval
4. Log all work in the appropriate folders
5. Update Dashboard.md after each task
6. Move completed items to Done/ with descriptive completion notes
