---
name: scheduler-trigger
description: Handle all time-based and recurring tasks triggered by cron or Task Scheduler. Manages daily briefings, weekly audits, periodic email polls, and business post generation.
---

# Scheduler Trigger: Recurring Tasks

Automate your day by handling periodic and time-based operations.

## When to Use
- **Scheduled Check**: Every morning at 8:00 AM.
- **Email Poll**: Every 30 minutes to check for urgent emails.
- **Daily Briefing**: Every weekday at 6:00 PM.
- **Weekly CEO Briefing**: Every Monday at 8:00 AM.
- **Subscription Audit**: First Monday of every month.

## Workflow: Processing a Schedule

1. **Trigger**: Receive a prompt with `SCHEDULED_TRIGGER: <type>`.
2. **Read**: Check `Tasks/schedules.md` for any special instructions.
3. **Execute**: Call the appropriate skill (e.g., `daily-briefing` for `daily_briefing`).
4. **Update**: Refresh `Dashboard.md` with the new completion metrics.
5. **Log**: Store the execution result in `Done/` and `Tasks/schedule_logs.md`.

## Silver Tier Schedules

| Type | Target Skill | Action |
|------|--------------|--------|
| `morning_checkin` | `vault-processor` | Triage `Needs_Action` and `Gmail`. |
| `daily_briefing` | `daily-briefing` | Summarize today's work and financials. |
| `weekly_ceo_briefing` | `daily-briefing` | Generate 7-day performance audit. |
| `email_poll` | `email-handler` | List unread emails and create action files. |
| `linkedin_post` | `linkedin-handler` | Generate and post business updates. |

## Rules
- **Silent Mode**: All scheduled tasks MUST run without user input.
- **Catch-Up**: If a task was missed, the next trigger should attempt to complete it.
- **No Overlap**: Ensure only one instance of a scheduled task is running.
- **Error Alerts**: If a scheduled task fails twice, create a `Needs_Action/` item for manual review.
