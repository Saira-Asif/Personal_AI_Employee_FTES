# Personal AI Employee - Bronze Tier

**Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.**

This is the Bronze Tier foundation for a Personal AI Employee - an autonomous AI agent that proactively manages your personal and business affairs using Qwen Code, Obsidian, and Python watcher scripts.

## What's Included (Bronze Tier)

✅ Obsidian vault with complete folder structure  
✅ Dashboard.md for real-time status tracking  
✅ Company_Handbook.md with Rules of Engagement  
✅ Business_Goals.md template for tracking objectives  
✅ FileSystem Watcher - monitors a drop folder for new files  
✅ Orchestrator - coordinates watchers and triggers Claude processing  
✅ Agent Skills for vault processing and daily briefings  
✅ Python project setup with uv support  

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Obsidian Vault                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Dashboard.md  │  Company_Handbook.md  │  Business_Goals.md │
│  └──────────────────────────────────────────────────────┘   │
│  ┌────────┐ ┌──────────────┐ ┌──────┐ ┌──────────────┐      │
│  │ Inbox/ │ │ Needs_Action/│ │ Done/│ │Pending_Approval│      │
│  └────────┘ └──────────────┘ └──────┘ └──────────────┘      │
│  ┌──────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │Accounting/   │ │Briefings/│ │  Plans/  │ │ Active_  │   │
│  │              │ │          │ │          │ │ Project/ │   │
│  └──────────────┘ └──────────┘ └──────────┘ └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                           ▲
                           │
┌──────────────────────────┴──────────────────────────┐
│                  Watchers Layer                      │
│  ┌───────────────────┐  ┌──────────────┐            │
│  │ FileSystemWatcher │  │ (More coming │            │
│  │ (Monitors Inbox/) │  │  in Silver)  │            │
│  └───────────────────┘  └──────────────┘            │
└─────────────────────────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────┐
│                  Orchestrator                        │
│  • Coordinates watchers                              │
│  • Detects new action items                          │
│  • Generates Claude prompts                          │
│  • Updates Dashboard                                 │
│  • Manages task lifecycle                            │
└─────────────────────────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────┐
│                 Qwen Code (You)                      │
│  • Processes items from Needs_Action/                │
│  • Creates plans for complex tasks                   │
│  • Executes work following Company Handbook rules    │
│  • Updates Dashboard on completion                   │
└─────────────────────────────────────────────────────┘
```

## Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| [Python](https://www.python.org/downloads/) | 3.13+ | Watcher scripts |
| [Qwen Code](https://qwenlm.ai/) | Latest | AI reasoning engine |
| [Obsidian](https://obsidian.md/download) | 1.10.6+ | Knowledge base & dashboard |
| [uv](https://docs.astral.sh/uv/) | Latest | Python package manager (recommended) |

## Quick Start

### 1. Install Python Dependencies

Using uv (recommended):
```bash
cd watchers
uv sync
```

Or using pip:
```bash
cd watchers
pip install -r requirements.txt
```

### 2. Open the Vault in Obsidian

1. Open Obsidian
2. Click "Open folder as vault"
3. Select the `AI_Employee_Vault` folder
4. Explore the pre-created files:
   - **Dashboard.md** - Your real-time status dashboard
   - **Company_Handbook.md** - AI Employee rules of engagement
   - **Business_Goals.md** - Your business objectives and metrics

### 3. Start the File System Watcher

The watcher monitors the `Inbox/` folder for new files:

```bash
cd watchers
python filesystem_watcher.py ../AI_Employee_Vault
```

Or with debug logging:
```bash
python filesystem_watcher.py ../AI_Employee_Vault --debug
```

### 4. Start the Orchestrator (Recommended)

The orchestrator coordinates watchers and processes items:

```bash
cd watchers
python orchestrator.py ../AI_Employee_Vault
```

This will:
- Start the FileSystemWatcher in the background
- Poll for new items in Needs_Action/ every 30 seconds
- Generate Qwen prompts for processing
- Update the Dashboard automatically

### 5. Use with Qwen Code

Point Qwen Code at your vault:

```bash
cd AI_Employee_Vault
# Launch Qwen Code
```

Then ask Qwen to:
- "Check Needs_Action for items to process"
- "Update the Dashboard with current status"
- "Generate a daily briefing"
- "Review Company_Handbook and confirm you understand the rules"

### 6. Test the System

Drop a test file into the Inbox:

```bash
# Create a test file
echo "This is a test task for my AI Employee" > AI_Employee_Vault/Inbox/test_task.txt
```

The FileSystemWatcher will detect it and create an action file in `Needs_Action/`. The orchestrator will then pick it up for processing.

## Folder Structure

```
AI_Employee_Vault/
├── Dashboard.md              # Real-time status overview
├── Company_Handbook.md       # Rules of engagement
├── Business_Goals.md         # Objectives and metrics
├── Inbox/                    # Drop files here for processing
├── Needs_Action/             # Items requiring processing
├── Done/                     # Completed tasks (archived)
├── Pending_Approval/         # Actions awaiting your approval
├── Accounting/               # Financial tracking
│   └── 2026-04/             # Current month
├── Briefings/                # Generated reports
├── Plans/                    # Multi-step task breakdowns
├── Active_Project/           # Work currently in progress
└── Tasks/
    ├── Active/               # Active tasks
    └── Done/                 # Completed tasks
```

## Demo: Bronze Tier in Action

### Quick Demo (2 minutes)

1. **Start the orchestrator** in one terminal:
   ```bash
   cd watchers
   python orchestrator.py ../AI_Employee_Vault
   ```

2. **Drop a file** into the Inbox in another terminal:
   ```bash
   echo "Please review this business proposal and create a summary." > ../AI_Employee_Vault/Inbox/proposal.txt
   ```

3. **Watch the magic happen:**
   - FileSystemWatcher detects the new file within 1 second
   - Creates `Needs_Action/FILE_<timestamp>_proposal.md` with metadata
   - Orchestrator picks it up and creates `Plans/PLAN_<timestamp>.md`
   - Dashboard.md updates with the new task count

4. **Check the results:**
   ```bash
   ls ../AI_Employee_Vault/Needs_Action/  # Action file created
   ls ../AI_Employee_Vault/Plans/          # Plan file created
   cat ../AI_Employee_Vault/Dashboard.md   # Updated metrics
   ```

### Full Validation Test

Run the end-to-end validation suite (36 checks across 9 categories):
```bash
cd watchers
python test_e2e.py --vault-path ../AI_Employee_Vault
```

Expected output: `64/64 tests passed` - Bronze Tier: FULLY VALIDATED

## How It Works

### The Workflow

1. **Input**: Drop files, messages, or tasks into `Inbox/`
2. **Detection**: FileSystemWatcher detects new files
3. **Action File Created**: Watcher creates `.md` file in `Needs_Action/`
4. **Processing**: Qwen Code (or orchestrator) picks up the item
5. **Work**: Task is moved to `Active_Project/` while being worked
6. **Completion**: Task moved to `Done/` with notes
7. **Update**: Dashboard.md is automatically updated

### File Drop Example

When you drop `report.pdf` into `Inbox/`, the watcher creates:

```markdown
# Needs_Action/FILE_20260410_143022_report.md

---
type: file_drop
original_name: report.pdf
file_type: document
created: 2026-04-10T14:30:22
status: pending
---

# File Dropped for Processing
...
```

### Claude → Qwen Processing Prompt

The orchestrator generates prompts like this for Qwen:

```
I need you to process this action file from my AI Employee vault.

## Action File: FILE_20260410_143022_report.md

## Content:
[... action file content ...]

## Your Task:
1. Read the Company_Handbook.md to understand your rules
2. Review this action file and determine what needs to be done
3. Execute the work according to the Company_Handbook rules
4. When complete, move to Done/ with completion notes
5. Update Dashboard.md with the results
```

## Agent Skills

Two skills are included for Qwen Code:

### vault-processor
Processes items from the vault - reads from Needs_Action, creates plans, executes tasks, and manages the workflow lifecycle.

### daily-briefing
Generates daily summaries and weekly "Monday Morning CEO Briefing" reports.

To use these skills, copy them into your Qwen Code skills directory or reference them when prompting Qwen.

## Configuration

### Watcher Settings

Edit `watchers/filesystem_watcher.py` to customize:

```python
# Change the check interval (default: 5 seconds for watchdog)
watcher = FileSystemWatcher(
    vault_path='/path/to/vault',
    watch_path='/path/to/watch'  # Default: vault/Inbox
)
```

### Orchestrator Settings

Edit `watchers/orchestrator.py` to customize:

```python
# Change poll interval (default: 30 seconds)
orchestrator.run(poll_interval=60)

# Add more watcher types
orchestrator = Orchestrator(
    vault_path='/path/to/vault',
    watcher_types=['fs', 'gmail']  # Future: add gmail, whatsapp, etc.
)
```

## Next Steps (Silver Tier)

### What You Have (Bronze)
- ✅ Local file system monitoring and processing
- ✅ Obsidian vault with dashboard, handbook, and goals
- ✅ Agent skills for vault processing and daily briefings
- ✅ Orchestrator with Claude prompt generation
- ✅ Complete folder structure with templates

### What's Next (Silver Tier)
To upgrade to Silver Tier, add:
- **Gmail Watcher** - Monitor inbox for important emails
- **WhatsApp Watcher** - Detect urgent messages via keywords
- **MCP servers** - Enable external actions (sending emails, posting to social media)
- **HITL approval workflow** - Automated approval/rejection cycle
- **Scheduled operations** - Daily briefings via cron/Task Scheduler
- **Auto Plan.md creation** - Claude reasoning loop for complex tasks

### Beyond Silver (Gold Tier)
- Full cross-domain integration (Personal + Business)
- Odoo Community accounting integration via MCP
- Facebook/Instagram/Twitter integration
- Weekly Business Audit with CEO Briefing
- Ralph Wiggum loop for autonomous multi-step completion
- Comprehensive audit logging

## Troubleshooting

### Watcher not detecting files
- Ensure the Inbox folder path is correct
- Check that watchdog is installed: `pip list | grep watchdog`
- Run with `--debug` flag to see detailed logs

### Orchestrator not processing items
- Verify Needs_Action folder has `.md` files
- Check file permissions on the vault folder
- Review orchestrator logs for errors

### Dashboard not updating
- Ensure Dashboard.md exists in vault root
- Check that orchestrator has write permissions
- Review Dashboard.md format (don't modify the frontmatter structure)

## Project Structure

```
Personal_AI_Employee_FTES/
├── AI_Employee_Vault/          # Obsidian vault
│   ├── Dashboard.md
│   ├── Company_Handbook.md
│   ├── Business_Goals.md
│   └── [folders...]
├── watchers/                   # Python watcher scripts
│   ├── base_watcher.py
│   ├── filesystem_watcher.py
│   ├── orchestrator.py
│   ├── pyproject.toml
│   └── requirements.txt
├── skills/                     # Qwen Code agent skills
│   ├── vault-processor/
│   │   └── SKILL.md
│   └── daily-briefing/
│       └── SKILL.md
├── QWEN.md                     # Project context
└── README.md                   # This file
```

## Resources

- [Full Hackathon Blueprint](./Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- [Qwen Code Documentation](https://qwenlm.ai/)
- [Agent Skills Documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Watchdog Documentation](https://python-watchdog.readthedocs.io/)

## License

This project is part of the Personal AI Employee Hackathon initiative.
