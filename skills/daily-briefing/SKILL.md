---
name: daily-briefing
description: Generate daily summaries, weekly CEO briefings, and subscription audits from vault activity data. Includes audit logging, configurable thresholds, and system health monitoring for Silver tier.
---

# Daily Briefing Skill

## Overview
This skill enables the AI Employee to generate comprehensive daily summaries and weekly "Monday Morning CEO Briefing" reports by analyzing vault activity, transactions, task completion data, and system health metrics.

## When to Use
- **Daily Briefing**: At end of each work day (6:00 PM) or via scheduler-trigger
- **Weekly CEO Briefing**: Every Monday morning (8:00 AM) or via scheduler-trigger
- **Subscription Audit**: First Monday of each month or on demand
- **On Demand**: When user requests a status update

## Data Sources
1. `Done/` folder - completed tasks
2. `Accounting/` folder - transactions
3. `Needs_Action/` folder - pending items
4. `Pending_Approval/` - awaiting approvals
5. `Active_Project/` - work in progress
6. `Business_Goals.md` - targets and metrics
7. `Company_Handbook.md` - escalation rules
8. `Tasks/approval_history.md` - HITL decisions
9. `Briefings/` - previous reports for comparison
10. MCP server status (if available) - API health

## Daily Briefing Generation

### Data Sources to Review
1. `Done/` folder - tasks completed today
2. `Accounting/` folder - any new transactions
3. `Needs_Action/` folder - pending items
4. `Pending_Approval/` - awaiting approvals (flag stale items)
5. `Active_Project/` - work in progress
6. `Business_Goals.md` - current targets and metrics
7. `Tasks/approval_history.md` - today's approval decisions

### Daily Briefing Template
```markdown
---
type: daily_briefing
date: <YYYY-MM-DD>
generated: <timestamp>
agent: gemini_code
data_sources: [Done/, Accounting/, Needs_Action/, Pending_Approval/, Active_Project/, Business_Goals.md]
---

# Daily Briefing - <Date>

## Summary
<Brief 2-3 sentence overview of the day>

## Tasks Completed
| Task | Time Completed | Source | Notes |
|------|---------------|--------|-------|
| <Task 1> | <HH:MM> | file_drop/gmail/whatsapp | <Details> |
| <Task 2> | <HH:MM> | file_drop/gmail/whatsapp | <Details> |

## Tasks Pending
| Task | Priority | Age | Blockers |
|------|----------|-----|----------|
| <Task 1> | <HIGH/MED/LOW> | <X hours> | <None/Details> |

## Financial Activity
- **Transactions Today**: <count>
- **Income**: $<amount>
- **Expenses**: $<amount>

## Approval Activity
- **Approved**: <count>
- **Rejected**: <count>
- **Auto-Approved**: <count>
- **Stale (>48h)**: <list>

## System Health
- **Last Email Poll**: <timestamp or "N/A">
- **Last WhatsApp Poll**: <timestamp or "N/A">
- **MCP Servers**: <healthy/degraded/down>
- **Watchers**: <running/stopped>

## Items Awaiting Approval
- <List any pending approvals with age>

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
6. `Tasks/approval_history.md` for approval metrics
7. MCP server logs for API health and uptime

### Weekly CEO Briefing Template
```markdown
---
type: ceo_briefing
period_start: <YYYY-MM-DD>
period_end: <YYYY-MM-DD>
generated: <timestamp>
agent: gemini_code
data_sources: [Done/, Accounting/, Briefings/, Business_Goals.md, Tasks/approval_history.md]
approval_metrics:
  total_approved: <count>
  total_rejected: <count>
  auto_approved: <count>
  expired: <count>
  avg_turnaround: <X hours>
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
  *Trend determination: week-over-week comparison, moving average*

### Month-to-Date
- **MTD Revenue**: $<amount>
- **vs Monthly Goal**: <X>% of $<goal>

### Key Transactions
| Date | Description | Amount | Type |
|------|-------------|--------|------|
| <...> | <...> | <...> | <Income/Expense> |

### Subscription Audit
<Review subscriptions for optimization>
- **<Service>**: <Observation>. Cost: $<amount>/month. <Suggested action>

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
- **<Service>**: <Observation>. Cost: $<amount>/month. <Suggested action>

### Efficiency Improvements
<Identify process improvements>
- **<Area>**: <Current issue>. <Suggested fix>

### Revenue Opportunities
<Identify potential revenue or business opportunities>
- **<Opportunity>**: <Description and potential value>

### Automation Opportunities
<Identify tasks that could be automated>
- **<Task>**: Currently manual, occurs <X> times/week. <Automation suggestion>

---

## Approval Activity
- **Total Approved**: <count>
- **Total Rejected**: <count>
- **Auto-Approved**: <count>
- **Expired**: <count>
- **Average Turnaround**: <X hours>

---

## Social Media Activity (if applicable)
| Platform | Posts This Week | Engagement Rate | Follower Change |
|----------|----------------|-----------------|-----------------|
| Facebook | <count> | <X>% | <+/-> |
| Instagram | <count> | <X>% | <+/-> |
| Twitter | <count> | <X>% | <+/-> |

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

## System Health
- **Briefing Reliability**: <X>/5 expected briefings generated this week>
- **MCP Server Uptime**: <X>% uptime this week>
- **Watcher Status**: <running/stopped/errors>
- **Error Rate**: <X> errors this week

---

## Recommended Actions for This Week
1. <Priority action 1>
2. <Priority action 2>
3. <Priority action 3>

---

_Briefing generated automatically by AI Employee_
```

## Analysis Logic

### Configurable Thresholds
Read thresholds from Business_Goals.md if available, otherwise use defaults:

| Threshold | Default | Config Key |
|-----------|---------|------------|
| Subscription inactivity | 30 days | subscription_inactive_days |
| Subscription cost increase | 20% | subscription_cost_increase_pct |
| Max monthly subscriptions | $500 | max_monthly_subscriptions |
| Bottleneck time multiplier | 2x | bottleneck_time_multiplier |
| Stale approval age | 48 hours | stale_approval_hours |
| Critical approval age | 4 hours | critical_approval_hours |

### Subscription Audit
When reviewing expenses:
1. Identify recurring payments
2. Check usage patterns (if available)
3. Flag if:
   - No activity in configured inactive days
   - Cost increased above configured threshold
   - Duplicate functionality exists
   - Total subscription costs exceed configured max

### Bottleneck Detection
Flag tasks as bottlenecks if:
- Took more than configured multiplier longer than expected
- Required multiple revision cycles
- Blocked other dependent tasks
- User had to intervene

### Proactive Suggestions
Generate suggestions based on patterns:
- Unused subscriptions → cancellation
- Recurring delays → process improvement
- Frequent task types → automation opportunity
- Expense spikes → investigation needed
- Slow approval turnaround → streamline process

## Audit Logging
Every briefing generated is logged:
```markdown
---
type: briefing_audit
generated: <timestamp>
briefing_type: <daily/weekly/subscription_audit>
agent: gemini_code
data_sources: <list of files consulted>
errors: <any errors encountered>
---
```
Save to `Tasks/briefing_audit_log.md`. Append-only.

## Rules
1. Be honest and direct in reporting
2. Include both wins and problems
3. Provide specific numbers, not vague statements
4. Always include actionable recommendations
5. Flag anything that violates Company_Handbook.md rules
6. Save all briefings to `Briefings/` folder with date prefix
7. Read thresholds from Business_Goals.md if available, use defaults otherwise
8. Include system health metrics in every briefing
9. Log every briefing to audit log
10. Compare against previous briefing to identify trends and changes
