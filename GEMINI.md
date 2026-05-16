# GEMINI.md - Personal AI Employee Context

This file provides foundational context, architectural overviews, and operational guidelines for the **Personal AI Employee (Bronze Tier)** project.

## Project Overview
The **Personal AI Employee** is a local-first, autonomous "Digital FTE" (Full-Time Equivalent) system. It is designed to manage personal and business affairs 24/7 by coordinating an LLM (Gemini/Qwen) with a local file-based workflow.

- **The Brain:** LLM reasoning engine (Gemini/Qwen) executing via terminal or agent skills.
- **The GUI & Memory:** [Obsidian](https://obsidian.md/) vault acting as a real-time dashboard and long-term memory.
- **The Senses (Watchers):** Python scripts monitoring inputs (Filesystem, Gmail, etc.) to trigger actions.
- **The Hands (MCP):** Model Context Protocol (MCP) servers for external actions (Email, Browser, Calendar).

### Core Architecture
- **Obsidian Vault (`AI_Employee_Vault/`):** The central source of truth. Data is stored in Markdown files with YAML frontmatter.
- **Watchers (`watchers/`):** Background Python processes that monitor for new inputs and create "Action Files" in `Needs_Action/`.
- **Orchestrator (`watchers/orchestrator.py`):** Coordinates watchers, generates LLM prompts, manages the task lifecycle, and updates the `Dashboard.md`.
- **Agent Skills (`skills/`):** Encapsulated capabilities for the AI (e.g., `vault-processor`, `daily-briefing`).

## Building and Running

### Prerequisites
- **Python:** 3.13+ (Required for watchers)
- **Node.js:** v24+ (Required for MCP servers)
- **Obsidian:** v1.10.6+ (For vault management and dashboard)

### Setup
Run the automated setup script or install manually:
```bash
# Windows Setup
./setup.bat

# Manual Setup
cd watchers
pip install -r requirements.txt
```

### Execution
To start the AI Employee system (Watchers + Orchestrator):
```bash
# From project root
python watchers/orchestrator.py ./AI_Employee_Vault
```

### Validation
Run the end-to-end test suite to verify the setup (36+ checks):
```bash
python watchers/test_e2e.py --vault-path ./AI_Employee_Vault
```

## Development Conventions

### 1. Vault Workflow
The system operates on a state-based file movement pattern:
- `Inbox/`: Drop zone for new files/inputs.
- `Needs_Action/`: Items detected by watchers requiring LLM processing.
- `Active_Project/`: Work currently being processed by the AI.
- `Pending_Approval/`: Actions requiring human intervention (HITL).
- `Done/`: Completed and archived tasks.
- `Plans/`: Multi-step task breakdowns created by the AI.

### 2. File Metadata (Frontmatter)
All action items and system files MUST use YAML frontmatter for tracking state and metadata:
```yaml
---
type: file_drop | email | task | plan
status: pending | in_progress | complete | approved
priority: LOW | MEDIUM | HIGH
created: YYYY-MM-DDTHH:MM:SS
---
```

### 3. Rules of Engagement
- **Company_Handbook.md:** Foundational rules. The AI MUST read this before processing any items.
- **Human-in-the-Loop (HITL):** Sensitive actions (payments, external comms) MUST NOT be executed automatically. Create an approval file in `Pending_Approval/` instead.
- **Dashboard Updates:** The `Dashboard.md` must be updated after every task completion to reflect real-time status.

### 4. Agent Skills
New capabilities should be implemented as **Agent Skills** in the `skills/` directory. Each skill contains a `SKILL.md` defining its workflow, rules, and triggers.

## Key Files
- `AI_Employee_Vault/Dashboard.md`: Real-time status overview.
- `AI_Employee_Vault/Company_Handbook.md`: AI rules of engagement.
- `watchers/orchestrator.py`: The main coordination engine.
- `watchers/filesystem_watcher.py`: File monitoring logic.
- `skills/vault-processor/SKILL.md`: Core logic for processing vault items.

## Tiered Progression
- **Bronze (Current):** Local filesystem monitoring, Obsidian dashboard, basic vault processing.
- **Silver:** External integrations (Gmail/WhatsApp), MCP servers, scheduled briefings.
- **Gold:** Autonomous multi-step loops (Ralph Wiggum), Odoo accounting, weekly CEO audits.
