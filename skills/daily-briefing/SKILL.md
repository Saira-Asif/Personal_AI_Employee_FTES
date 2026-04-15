---
name: daily-briefing
description: Generate daily summaries and weekly CEO briefings from vault activity data
---

# Daily Briefing Skill

## Overview
This skill enables the AI Employee to generate comprehensive daily summaries and weekly "Monday Morning CEO Briefing" reports by analyzing vault activity, transactions, and task completion data.

## When to Use
- **Daily Briefing**: At end of each work day (6:00 PM)
- **Weekly CEO Briefing**: Every Monday morning (8:00 AM)
- **On Demand**: When user requests a status update

## Daily Briefing Generation

### Data Sources to Review
1. `Done/` folder - tasks completed today
2. `Accounting/` folder - any new transactions
3. `Needs_Action/` folder - pending items
4. `Pending_Approval/` - awaiting approvals
5. `Active_Project/` - work in progress
6. `Business_Goals.md` - current targets and metrics

### Daily Briefing Template
```markdown
---
type: daily_briefing
date: <YYYY-MM-DD>
generated: <timestamp>
---

# Daily Briefing - <Date>

## Summary
<Brief 2-3 sentence overview of the day>

## Tasks Completed
| Task | Time Completed | Notes |
|------|---------------|-------|
| <Task 1> | <HH:MM> | <Details> |
| <Task 2> | <HH:MM> | <Details> |

## Tasks Pending
| Task | Priority | Age | Blockers |
|------|----------|-----|----------|
| <Task 1> | <HIGH/MED/LOW> | <X hours> | <None/Details> |

## Financial Activity
- **Transactions Today**: <count>
- **Income**: $<amount>
- **Expenses**: $<amount>

## Items Awaiting Approval
- <List any pending approvals>

## Tomorrow's Priorities
1. <Priority 1>
2. <Priority 2>
3. <Priority 3>

## Notes
<Any additional context or observations>
```

## Weekly CEO Briefing Generation

### Data Sources to Review
1. All `Done/` files from the past week
2. `Accounting/` transactions for the week
3. `Briefings/` previous week's briefing for comparison
4. `Business_Goals.md` for targets vs actuals
5. `Company_Handbook.md` for escalation rules

### Weekly CEO Briefing Template
```markdown
---
type: ceo_briefing
period_start: <YYYY-MM-DD>
period_end: <YYYY-MM-DD>
generated: <timestamp>
---

# Monday Morning CEO Briefing

## Period: <Start Date> to <End Date>

---

## Executive Summary
<3-5 sentence high-level overview of the week>

---

## Revenue & Financials

### This Week
- **Revenue**: $<amount>
- **vs Target**: <+/-%> 
- **Trend**: <Improving/Stable/Declining>

### Month-to-Date
- **MTD Revenue**: $<amount>
- **vs Monthly Goal**: <X>% of $<goal>

### Key Transactions
| Date | Description | Amount | Type |
|------|-------------|--------|------|
| <...> | <...> | <...> | <Income/Expense> |

---

## Task Performance

### Completed This Week
- [x] <Task 1>
- [x] <Task 2>
- [x] <Task 3>

**Total Tasks Completed**: <count>
**vs Weekly Target**: <+/->

### Bottlenecks Identified
| Task | Expected Time | Actual Time | Delay | Root Cause |
|------|--------------|-------------|-------|------------|
| <...> | <...> | <...> | <...> | <...> |

---

## Proactive Suggestions

### Cost Optimization
<Review subscriptions and expenses for optimization opportunities>
- **<Service>**: <Observation>. <Suggested action>

### Efficiency Improvements
<Identify process improvements>
- **<Area>**: <Current issue>. <Suggested fix>

### Revenue Opportunities
<Identify potential revenue or business opportunities>
- **<Opportunity>**: <Description and potential value>

---

## Upcoming Deadlines (Next 2 Weeks)
| Project/Task | Due Date | Days Remaining | Status |
|--------------|----------|----------------|--------|
| <...> | <...> | <...> | <On Track/At Risk> |

---

## Business Goals Progress

### Q2 2026 Targets
| Metric | Target | Current | Progress |
|--------|--------|---------|----------|
| Monthly Revenue | $10,000 | $<amount> | <X>% |
| Tasks/Week | 20 | <count> | <X>% |
| Client Response Time | <24h | <actual> | <status> |

---

## Recommended Actions for This Week
1. <Priority action 1>
2. <Priority action 2>
3. <Priority action 3>

---

_Briefing generated automatically by AI Employee_
```

## Analysis Logic

### Subscription Audit
When reviewing expenses:
1. Identify recurring payments
2. Check usage patterns (if available)
3. Flag if:
   - No activity in 30 days
   - Cost increased > 20%
   - Duplicate functionality exists
   - Total subscription costs exceed $500/month

### Bottleneck Detection
Flag tasks as bottlenecks if:
- Took 2x longer than expected
- Required multiple revision cycles
- Blocked other dependent tasks
- User had to intervene

### Proactive Suggestions
Generate suggestions based on patterns:
- Unused subscriptions → cancellation
- Recurring delays → process improvement
- Frequent task types → automation opportunity
- Expense spikes → investigation needed

## Rules
1. Be honest and direct in reporting
2. Include both wins and problems
3. Provide specific numbers, not vague statements
4. Always include actionable recommendations
5. Flag anything that violates Company_Handbook.md rules
6. Save all briefings to `Briefings/` folder with date prefix
