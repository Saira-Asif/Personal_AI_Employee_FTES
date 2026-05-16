---
name: vault-processor
description: Core autonomous reasoning loop for processing items from Needs_Action. Creates multi-step Plan.md files, coordinates with Silver tier skills, and manages the task lifecycle until completion.
---

# Vault Processor: Autonomous Reasoning Loop

Process any item from `Needs_Action/` to completion by creating plans and executing work.

## When to Use
- **Action Required**: When new items appear in `Needs_Action/`.
- **Complex Tasks**: When a task cannot be completed in a single step.
- **Task Triage**: To classify and prioritize incoming work.
- **Workflow Orchestration**: To coordinate between Email, WhatsApp, and HITL skills.

## Autonomous Workflow

1. **Scan**: Read `Needs_Action/` to identify the most urgent item.
2. **Context**: Read `Company_Handbook.md` and `Business_Goals.md`.
3. **Plan**: If complex, create `Plans/PLAN_<desc>_<timestamp>.md`.
4. **Execute**: Perform actions (using other skills if needed).
5. **Approve**: If sensitive, use `hitl-manager` to request approval.
6. **Finalize**: Move to `Done/` and update `Dashboard.md`.

## Planning (Plan.md)

Always create a plan for multi-step tasks:

```markdown
---
type: plan
created: <YYYY-MM-DD HH:MM>
status: in_progress
priority: <HIGH|MEDIUM|LOW>
---

# Plan: <Objective>

## Steps
- [ ] 1. <Step description>
- [ ] 2. <Step description> (Requires HITL)
- [ ] 3. <Step description>

## Notes
<Context or constraints>
```

## Dashboard Updates

Update `Dashboard.md` using this pattern:
1. Read current `Dashboard.md`.
2. Update metrics (Pending Tasks, Completed Today).
3. Append recent activity to the log.
4. Save file.

## Rules
- **Handbook First**: Always read `Company_Handbook.md` before processing any item.
- **Claim-by-Move**: Move items to `Active_Project/` immediately to signal "In Progress".
- **Zero-Bypass HITL**: Sensitive actions MUST use the `hitl-manager` skill.
- **Clean Exit**: Only move to `Done/` when the final verification step is complete.
