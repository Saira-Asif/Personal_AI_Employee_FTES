---
name: scheduler-trigger
description: Handle scheduled and recurring tasks triggered by cron or Task Scheduler. Manages daily briefings, weekly audits, periodic email checks, and time-based task deadlines.
---

# Scheduler Trigger Skill

## Overview
This skill enables the AI Employee to handle time-based and recurring operations. It processes scheduled triggers from cron (Mac/Linux) or Task Scheduler (Windows) and executes the appropriate workflows at the right time.

## When to Use
- When cron or Task Scheduler fires a scheduled trigger
- When processing time-based recurring tasks (daily briefing, weekly audit, periodic checks)
- When checking if scheduled tasks are running on time
- When generating reports at specific times

## Supported Schedules

### Built-in Schedules (Silver Tier Defaults)

| Schedule | Frequency | Trigger | Action |
|----------|-----------|---------|--------|
| Daily Briefing | Weekdays at 6:00 PM | cron/Task Scheduler | Generate daily briefing report |
| Morning Check-in | Daily at 8:00 AM | cron/Task Scheduler | Check Inbox, Needs_Action, emails |
| Weekly CEO Briefing | Mondays at 8:00 AM | cron/Task Scheduler | Generate comprehensive weekly report |
| Email Poll | Every 30 min (business hours) | cron/Task Scheduler | Check Gmail via MCP |
| Subscription Audit | First Monday of each month | cron/Task Scheduler | Review all subscriptions |
| Dashboard Refresh | Every 2 hours | cron/Task Scheduler | Update Dashboard.md with current stats |

### Custom Schedules
Users can add custom schedules to `Tasks/schedules.md`:
```markdown
---
type: schedule
created: <timestamp>
status: active
---

# Custom Schedule

## Task Name
<Descriptive name>

## Frequency
<cron expression or description>

## Action
<What should be done>

## Priority
<HIGH/MEDIUM/LOW>
```

## Workflow

### 1. Receive Scheduled Trigger
```
1. Cron/Task Scheduler calls Qwen Code with a scheduled prompt
2. Qwen reads the trigger type from the prompt
3. Execute the appropriate workflow
4. Log the execution result
5. Update Dashboard.md if applicable
```

### 2. Process by Trigger Type

#### Daily Briefing (Weekdays 6:00 PM)
```
1. Read all Done/ files created today
2. Check Accounting/ for today's transactions
3. Review Pending_Approval/ for stale items
4. Generate daily briefing using daily-briefing skill template
5. Save to Briefings/YYYY-MM-DD_Daily_Briefing.md
6. Update Dashboard.md with "Daily briefing generated"
```

#### Morning Check-in (Daily 8:00 AM)
```
1. Scan Inbox/ and Needs_Action/ for overnight items
2. Check Gmail via MCP for unread messages
3. Review Business_Goals.md for today's deadlines
4. Create action files for any new items found
5. Generate a morning summary in Briefings/YYYY-MM-DD_Morning_Checkin.md
6. Alert user if CRITICAL items are pending
```

#### Weekly CEO Briefing (Mondays 8:00 AM)
```
1. Use daily-briefing skill to generate weekly report
2. Review all Done/ files from past week
3. Analyze Accounting/ transactions for the week
4. Compare against Business_Goals.md targets
5. Identify bottlenecks, cost optimizations, opportunities
6. Save to Briefings/YYYY-MM-DD_CEO_Briefing.md
7. Update Dashboard.md with weekly summary
```

#### Email Poll (Every 30 min, 8 AM - 6 PM)
```
1. Check Gmail MCP for new unread messages
2. Classify each email by priority (use email-handler skill rules)
3. Create action files for CRITICAL/HIGH priority emails
4. Archive LOW priority emails
5. Do not alert user unless CRITICAL items found
```

#### Subscription Audit (Monthly, First Monday)
```
1. Read Accounting/ transactions for past 30 days
2. Identify recurring payments (subscriptions)
3. For each subscription:
   - Check if used in last 30 days
   - Check if cost increased > 20%
   - Check for duplicate functionality
4. Flag suspicious items for review
5. Create Pending_Approval/ items for cancellations
6. Save audit to Briefings/YYYY-MM_Subscription_Audit.md
```

### 3. Handle Missed Schedules
If a scheduled task was missed:
1. Check if the trigger fired at all (check Briefings/ for output)
2. If missed, create a catch-up action in Needs_Action/
3. Log the missed schedule to Dashboard.md
4. Do not double-execute (check timestamps)

### 4. Schedule Health Monitoring
Every 2 hours (Dashboard Refresh):
```
1. Count tasks completed today vs yesterday
2. Check if daily briefing was generated
3. Verify watchers are still running
4. Update Dashboard.md with:
   - Last briefing timestamp
   - Last email poll timestamp
   - Current Needs_Action count
   - System status (healthy/degraded/down)
```

## Cron Setup Examples

### Mac/Linux (crontab -e)
```cron
# Daily briefing at 6:00 PM on weekdays
0 18 * * 1-5 cd /path/to/AI_Employee_Vault && qwen --prompt "SCHEDULED_TRIGGER: daily_briefing"

# Morning check-in at 8:00 AM daily
0 8 * * * cd /path/to/AI_Employee_Vault && qwen --prompt "SCHEDULED_TRIGGER: morning_checkin"

# Weekly CEO briefing on Mondays at 8:00 AM
0 8 * * 1 cd /path/to/AI_Employee_Vault && qwen --prompt "SCHEDULED_TRIGGER: weekly_ceo_briefing"

# Email poll every 30 min during business hours
*/30 8-17 * * 1-5 cd /path/to/AI_Employee_Vault && qwen --prompt "SCHEDULED_TRIGGER: email_poll"
```

### Windows (Task Scheduler)
Create tasks with these settings:
- **Trigger**: Daily, recurring
- **Action**: `qwen --prompt "SCHEDULED_TRIGGER: <trigger_type>"`
- **Start in**: `C:\path\to\AI_Employee_Vault`
- **Run whether user is logged on or not**: Yes

## Scheduled Task Prompt Format
All scheduled triggers use this format:
```
SCHEDULED_TRIGGER: <trigger_type>

Please execute the scheduled task according to the scheduler-trigger skill.
Current time: <YYYY-MM-DD HH:MM:SS>
```

Valid trigger types: `daily_briefing`, `morning_checkin`, `weekly_ceo_briefing`, `email_poll`, `subscription_audit`, `dashboard_refresh`

## Rules
1. Scheduled tasks should run silently (no interactive prompts)
2. If a scheduled task fails, log the error and create a catch-up item
3. Never send emails or messages from scheduled tasks without approval
4. Daily briefings should be generated even if no activity occurred
5. Morning check-in should alert user only for CRITICAL items
6. Always check Company_Handbook.md before executing any scheduled action
7. If Qwen Code is unavailable, watchers continue collecting data for later processing
