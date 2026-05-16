"""
Trigger LinkedIn Post - Drops a task file into Needs_Action to trigger Gemini to draft a sales post.
Designed to be called by a scheduler (cron/Task Scheduler).
"""

import sys
from pathlib import Path
from datetime import datetime

def trigger_post_draft(vault_path: str):
    vault = Path(vault_path)
    needs_action = vault / 'Needs_Action'
    
    if not needs_action.exists():
        print(f"Error: Vault path {vault_path} invalid or missing Needs_Action/")
        return False

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"TASK_linkedin_post_{timestamp}.md"
    filepath = needs_action / filename
    
    content = f"""---
type: task
created: {datetime.now().isoformat()}
status: pending
priority: MEDIUM
source: scheduler
---

# Draft LinkedIn Sales Post

## Objective
Generate a professional LinkedIn post to drive sales and business engagement based on current goals.

## Required Actions
- [ ] Review `Business_Goals.md` for current focus (services, products, or wins)
- [ ] Consult `Company_Handbook.md` for brand voice
- [ ] Draft a high-engagement post (Value-Add, Question, or Promotion)
- [ ] Create an approval request in `Pending_Approval/` using the LinkedIn template
- [ ] Move this task to `Done/` once the draft is created

"""
    filepath.write_text(content, encoding='utf-8')
    print(f"LinkedIn post task triggered: {filename}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python trigger_linkedin_post.py <vault_path>")
        sys.exit(1)
    
    success = trigger_post_draft(sys.argv[1])
    sys.exit(0 if success else 1)
