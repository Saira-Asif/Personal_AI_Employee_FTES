"""
Trigger Daily Briefing - Drops a task file into Needs_Action to trigger the AI briefing.
Designed to be called by a scheduler (cron/Task Scheduler).
"""

import sys
from pathlib import Path
from datetime import datetime

def trigger_briefing(vault_path: str):
    vault = Path(vault_path)
    needs_action = vault / 'Needs_Action'
    
    if not needs_action.exists():
        print(f"Error: Vault path {vault_path} invalid or missing Needs_Action/")
        return False

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"TASK_daily_briefing_{timestamp}.md"
    filepath = needs_action / filename
    
    content = f"""---
type: task
created: {datetime.now().isoformat()}
status: pending
priority: HIGH
source: scheduler
---

# Generate Daily Briefing

## Objective
Analyze today's activity and generate a comprehensive Daily Briefing in the `Briefings/` folder.

## Required Actions
- [ ] Review `Done/` for tasks completed today
- [ ] Review `Accounting/` for new transactions
- [ ] Review `Needs_Action/` and `Pending_Approval/` for status
- [ ] Generate the briefing using the template in `skills/daily-briefing/SKILL.md`
- [ ] Update `Dashboard.md` with current metrics
- [ ] Move this task to `Done/` when complete

"""
    filepath.write_text(content, encoding='utf-8')
    print(f"Daily briefing task triggered: {filename}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python trigger_daily_briefing.py <vault_path>")
        sys.exit(1)
    
    success = trigger_briefing(sys.argv[1])
    sys.exit(0 if success else 1)
