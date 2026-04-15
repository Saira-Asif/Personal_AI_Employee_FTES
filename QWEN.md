# Personal AI Employee FTEs - Project Context

## Project Overview

This repository contains the complete **Bronze Tier** implementation of the Personal AI Employee Hackathon - an autonomous "Digital FTE" (Full-Time Equivalent AI agent) that proactively manages personal and business affairs 24/7.

The system uses:
- **Qwen Code** as the primary reasoning/execution engine
- **Obsidian** as the local-first knowledge base and management dashboard
- **Python Sentinel Scripts** ("Watchers") for monitoring file system inputs
- **Model Context Protocol (MCP)** server placeholders for future external actions (Silver+)

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Obsidian Vault                            │
│  Dashboard.md │ Company_Handbook.md │ Business_Goals.md          │
│  Inbox/ │ Needs_Action/ │ Done/ │ Pending_Approval/              │
│  Accounting/ │ Briefings/ │ Plans/ │ Active_Project/             │
│  Tasks/ │ Templates/                                           │
└─────────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────┴────────────────────────────────────┐
│                      Watchers Layer                               │
│  FileSystemWatcher (watchdog) - monitors Inbox/ for new files     │
│  Creates .md action files in Needs_Action/                        │
└──────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────┴────────────────────────────────────┐
│                       Orchestrator                                │
│  Coordinates watchers │ Detects new items │ Generates Claude      │
│  prompts │ Manages task lifecycle │ Updates Dashboard             │
└──────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────┴────────────────────────────────────┐
│                    Qwen Code + Agent Skills                     │
│  vault-processor skill │ daily-briefing skill                     │
│  Processes items │ Creates plans │ Executes work                  │
└──────────────────────────────────────────────────────────────────┘
```

## Complete File Structure

```
Personal_AI_Employee_FTES/
├── .qwen/                            # Qwen Code configuration
│   ├── settings.json                 # Permission settings
│   └── CLAUDE.md                     # AI Employee instructions
├── .qwen/skills/                     # Qwen Code skills
├── AI_Employee_Vault/                # Obsidian vault
│   ├── .obsidian/                    # Obsidian workspace settings
│   │   ├── app.json
│   │   ├── appearance.json
│   │   ├── core-plugins.json
│   │   └── workspace.json
│   ├── Dashboard.md                  # Real-time status dashboard
│   ├── Company_Handbook.md           # Rules of engagement
│   ├── Business_Goals.md             # Objectives and metrics
│   ├── Inbox/                        # Drop zone for new inputs
│   ├── Needs_Action/                 # Items requiring processing
│   ├── Done/                         # Completed tasks (archived)
│   ├── Pending_Approval/             # Actions awaiting user approval
│   ├── Accounting/                   # Financial tracking
│   │   └── 2026-04/
│   │       └── transactions.md       # Current month transactions
│   ├── Briefings/                    # Generated reports
│   ├── Plans/                        # Multi-step task breakdowns
│   ├── Active_Project/               # Work currently in progress
│   ├── Tasks/                        # Task management
│   │   ├── Active/
│   │   ├── Done/
│   │   └── task_tracker.md           # Active task tracker
│   └── Templates/                    # Reusable file templates
│       ├── Task.md
│       ├── Email.md
│       ├── Approval_Request.md
│       └── Plan.md
├── watchers/                         # Python watcher scripts
│   ├── __init__.py
│   ├── base_watcher.py               # Abstract base class
│   ├── filesystem_watcher.py         # File system monitoring (watchdog)
│   ├── orchestrator.py               # Coordinator for watchers + Claude
│   ├── setup.py                      # Setup and validation script
│   ├── test_e2e.py                   # End-to-end validation (36 checks across 9 categories)
│   ├── pyproject.toml                # Python project config (uv)
│   └── requirements.txt              # Python dependencies
├── skills/                           # Qwen Code agent skills
│   ├── vault-processor/
│   │   └── SKILL.md                  # Process vault items
│   └── daily-briefing/
│       └── SKILL.md                  # Generate daily/weekly reports
├── mcp-servers/                      # MCP server configs (Silver+)
│   ├── mcp-config.json               # Server configuration templates
│   └── README.md                     # MCP setup guide
├── scripts/                          # Utility scripts
├── .gitattributes                    # Git text normalization
├── .gitignore                        # Ignore secrets and temp files
├── setup.bat                         # Windows setup script
├── skills-lock.json                  # Skills version lock
├── QWEN.md                           # This file
├── README.md                         # User-facing documentation
└── Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md
```

## Bronze Tier Deliverables (All Complete)

| Requirement | Status | Implementation |
|-------------|--------|---------------|
| Obsidian vault with Dashboard.md and Company_Handbook.md | Done | Full vault with 3 core files + workspace config |
| One working Watcher script | Done | FileSystemWatcher with watchdog library |
| Qwen Code reading/writing to vault | Done | Orchestrator generates prompts, skills define behavior |
| Basic folder structure: /Inbox, /Needs_Action, /Done | Done | 9 folders + Templates + Tasks + Accounting |
| AI functionality as Agent Skills | Done | vault-processor + daily-briefing skills |

## Key Components

### 1. Watchers (Perception Layer)
- **base_watcher.py** - Abstract base class all watchers inherit from
- **filesystem_watcher.py** - Monitors Inbox/ using watchdog library, creates action files in Needs_Action/

### 2. Orchestrator (Coordination Layer)
- **orchestrator.py** - Coordinates watchers, generates Claude prompts, manages task lifecycle (pending → in_progress → complete), auto-updates Dashboard

### 3. Agent Skills (Reasoning Layer)
- **vault-processor** - Processes items from Needs_Action, creates plans, executes work, manages the full workflow
- **daily-briefing** - Generates daily summaries and weekly "Monday Morning CEO Briefing" reports

### 4. Vault (Memory/GUI Layer)
- **Dashboard.md** - Real-time metrics, task counts, system status
- **Company_Handbook.md** - Complete rules of engagement (identity, escalation triggers, financial rules, error handling)
- **Business_Goals.md** - Revenue targets, KPIs, active projects, subscription tracking

## Setup Commands

```bash
# Windows (one-click)
setup.bat

# Or manually:
cd watchers
pip install -r requirements.txt

# Validate (36 checks across 9 categories)
python test_e2e.py --vault-path /path/to/AI_Employee_Vault

# Run the orchestrator
python orchestrator.py ../AI_Employee_Vault
```

## How It Works

1. **Drop** a file into `AI_Employee_Vault/Inbox/`
2. **FileSystemWatcher** detects it and creates an action file in `Needs_Action/`
3. **Orchestrator** picks up the action file, creates a plan, generates a Qwen prompt
4. **Qwen Code** processes the item (following Company_Handbook rules)
5. **Completed** items move to `Done/` with notes, Dashboard updates automatically

## Workflow Pattern

```
Input → Inbox/ → FileSystemWatcher detects → Needs_Action/*.md
         ↓
Orchestrator picks up → Creates plan in Plans/
         ↓
Claude processes (following handbook rules)
         ↓
Move to Done/ with completion notes → Update Dashboard.md
```

## Security Rules

- Vault sync includes only markdown/state - secrets never sync
- `.env`, tokens, WhatsApp sessions, banking credentials are gitignored
- Human-in-the-loop required for sensitive actions (create files in Pending_Approval/ instead of acting directly)
- Claim-by-move rule: first agent to move item from Needs_Action/ to Active_Project/ owns it

## Development Conventions

- **Local-first**: All data stored locally in Obsidian vault
- **Markdown-based**: All state, tasks, reports use `.md` files with YAML frontmatter
- **File-based communication**: Agents communicate by writing files into shared folders
- **Single-writer rule**: Only Local writes to Dashboard.md
- **Naming convention**: `TYPE_description_timestamp.md`

## Technologies

| Component | Technology |
|-----------|------------|
| Reasoning Engine | Qwen Code |
| Dashboard/Knowledge Base | Obsidian (local Markdown) |
| Watcher Scripts | Python 3.13+, watchdog |
| Package Manager | uv (recommended) or pip |
| Agent Skills | Qwen Code SKILL.md format |
| Version Control | Git + GitHub Desktop |
| Scheduling (future) | cron (Mac/Linux) or Task Scheduler (Windows) |

## Next Tiers

- **Silver**: Gmail/WhatsApp watchers, MCP servers, HITL automation, scheduling
- **Gold**: Full cross-domain, Odoo accounting, weekly audits, Ralph Wiggum loop
- **Platinum**: Cloud VM 24/7, work-zone specialization, synced vault

## Weekly Research Meeting

- **When**: Every Wednesday at 10:00 PM on Zoom
- **Zoom**: https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1
- **Meeting ID**: 871 8870 7642 | **Passcode**: 744832
- **YouTube**: https://www.youtube.com/@panaversity

## Resources

- [Full Hackathon Blueprint](./Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- [Qwen Code Documentation](https://qwenlm.ai/)
- [Agent Skills Documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Ralph Wiggum Plugin](https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum)
- [Watchdog Documentation](https://python-watchdog.readthedocs.io/)
