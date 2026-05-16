---
name: daily-briefing
description: Generate comprehensive daily summaries and weekly CEO reports. Audits transaction data, task completion rates, and system health metrics for business oversight.
---

# Daily Briefing: Business Oversight

Generate insightful summaries and audits for your personal and business affairs.

## When to Use
- **Daily Wrap-up**: Every weekday at 6:00 PM (via `scheduler-trigger`).
- **Monday Briefing**: Every Monday at 8:00 AM (via `scheduler-trigger`).
- **Audit Request**: When the user asks for a "status update" or "audit".

## Workflow: Daily Summary

1. **Collect**: Read all `Done/` files created today.
2. **Metrics**: Count tasks completed and count unread emails.
3. **Financials**: Scan `Accounting/` for new transactions.
4. **Draft**: Create `Briefings/YYYY-MM-DD_Daily_Briefing.md` using the standard template.
5. **Update**: Update `Dashboard.md` with the latest summary.

## Workflow: Weekly CEO Briefing

1. **Trend Analysis**: Compare this week's `Done/` tasks against the previous week.
2. **Revenue Audit**: Analyze weekly income vs `Business_Goals.md` targets.
3. **Bottlenecks**: Identify tasks that took longer than 2x the average time.
4. **Suggestions**: Provide 2-3 proactive suggestions for business growth or cost saving.
5. **Report**: Save to `Briefings/YYYY-MM-DD_CEO_Briefing.md`.

## Standard Briefing Template
```markdown
---
type: briefing
kind: <daily|weekly>
generated: <timestamp>
---

# <Daily|Weekly> Briefing - <Date>

## Summary
<2-3 sentences on overall status>

## Key Accomplishments
- <Task A>
- <Task B>

## Financial Status
- **Income**: $<amount>
- **Expenses**: $<amount>

## Bottlenecks & Issues
- <Issue description>

## Recommendations
- <Suggestion A>
```

## Rules
- **Data-Driven**: Never guess; all reports must be based on data found in the vault.
- **Honesty**: Report both wins and losses accurately.
- **Actionable**: Every report must end with at least one recommended action.
- **Archive**: Never overwrite old briefings; always create new files with dates.
