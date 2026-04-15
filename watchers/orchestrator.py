"""
Orchestrator - Coordinates watchers and triggers Qwen Code processing.

The Orchestrator:
1. Manages one or more watcher processes
2. Detects when new action files are created in Needs_Action/
3. Triggers Qwen Code to process the items
4. Monitors completion and moves items to Done/
5. Updates the Dashboard.md with status changes

For Bronze Tier: Coordinates the FileSystemWatcher with Qwen Code processing.

Usage:
    python orchestrator.py /path/to/vault

Or with specific watchers:
    python orchestrator.py /path/to/vault --watchers fs
"""

import sys
import time
import signal
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))


class Orchestrator:
    """
    Main orchestrator class that coordinates watchers and Qwen processing.
    """
    
    def __init__(self, vault_path: str, watcher_types: list = None):
        """
        Initialize the orchestrator.
        
        Args:
            vault_path: Path to the Obsidian vault root
            watcher_types: List of watcher types to enable (default: ['fs'])
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        self.active_project = self.vault_path / 'Active_Project'
        self.plans = self.vault_path / 'Plans'
        self.dashboard = self.vault_path / 'Dashboard.md'
        
        # Ensure directories exist
        for d in [self.needs_action, self.done, self.active_project, self.plans]:
            d.mkdir(parents=True, exist_ok=True)
        
        self.watcher_types = watcher_types or ['fs']
        self.watchers = []
        self.running = False
        self.processed_files = set()
        
        # Setup logging
        self.logger = logging.getLogger('Orchestrator')
        
        # Track stats
        self.stats = {
            'items_processed': 0,
            'items_completed': 0,
            'errors': 0,
            'start_time': None,
        }
    
    def setup_watchers(self):
        """Initialize and configure all requested watchers."""
        from filesystem_watcher import FileSystemWatcher
        
        if 'fs' in self.watcher_types:
            self.logger.info('Setting up FileSystemWatcher...')
            fs_watcher = FileSystemWatcher(
                vault_path=str(self.vault_path),
                watch_path=str(self.vault_path / 'Inbox')
            )
            self.watchers.append(('fs', fs_watcher))
            self.logger.info('FileSystemWatcher ready')
        
        # Future watchers can be added here:
        # if 'gmail' in self.watcher_types:
        #     from gmail_watcher import GmailWatcher
        #     ...
        
        self.logger.info(f'Initialized {len(self.watchers)} watcher(s)')
    
    def start_watchers(self):
        """Start all watchers in background threads."""
        import threading
        
        for name, watcher in self.watchers:
            thread = threading.Thread(
                target=watcher.start,
                name=f'{name}-watcher',
                daemon=True
            )
            thread.start()
            self.logger.info(f'Started {name} watcher in background thread')
    
    def check_for_new_items(self) -> list:
        """
        Check Needs_Action folder for unprocessed items.
        
        Returns:
            List of Path objects for new action files
        """
        new_items = []
        
        if not self.needs_action.exists():
            return new_items
        
        for action_file in self.needs_action.glob('*.md'):
            if str(action_file) not in self.processed_files:
                new_items.append(action_file)
        
        return new_items
    
    def process_item(self, action_file: Path) -> bool:
        """
        Process a single action file.
        
        This method:
        1. Reads the action file
        2. Determines what type of work is needed
        3. Moves to Active_Project/ while working
        4. Creates a plan if needed
        5. Executes the work (for Bronze tier, provides guidance for Qwen)
        6. Moves to Done/ with completion notes
        
        Args:
            action_file: Path to the action file
            
        Returns:
            True if successfully processed
        """
        self.logger.info(f'Processing: {action_file.name}')
        
        try:
            # Read the action file
            content = action_file.read_text(encoding='utf-8')
            
            # Parse the frontmatter to determine type
            if 'type: file_drop' in content:
                self._process_file_drop(action_file, content)
            elif 'type: email' in content:
                self._process_email(action_file, content)
            else:
                self._process_generic(action_file, content)
            
            self.stats['items_processed'] += 1
            self.processed_files.add(str(action_file))
            
            return True
            
        except Exception as e:
            self.stats['errors'] += 1
            self.logger.error(f'Error processing {action_file.name}: {e}')
            return False
    
    def _process_file_drop(self, action_file: Path, content: str):
        """Process a file drop action item."""
        # For Bronze tier: Create a processing plan and provide guidance
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        plan_content = f"""---
type: plan
created: {datetime.now().isoformat()}
status: in_progress
priority: MEDIUM
---

# Plan: Process Dropped File

## Objective
Review and categorize the dropped file, determine required actions.

## Steps
- [ ] Read the dropped file contents
- [ ] Identify the file type and purpose
- [ ] Determine if action is required
- [ ] If action needed, create specific task plan
- [ ] If no action, file appropriately
- [ ] Move original action file to Done/

## File Reference
- Action File: {action_file.name}

"""
        # Create plan file
        plan_file = self.plans / f'PLAN_process_file_{timestamp}.md'
        plan_file.write_text(plan_content, encoding='utf-8')
        self.logger.info(f'Created plan: {plan_file.name}')
    
    def _process_email(self, action_file: Path, content: str):
        """Process an email action item."""
        # For Bronze tier: Flag for review and create task
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        task_content = f"""---
type: task
created: {datetime.now().isoformat()}
status: pending
priority: HIGH
source: {action_file.name}
---

# Email Review Required

## Details
See attached action file for full email content.

## Required Actions
- [ ] Read email content
- [ ] Determine appropriate response
- [ ] Draft response if needed (requires approval to send)
- [ ] File or archive email

"""
        task_file = self.needs_action / f'TASK_email_review_{timestamp}.md'
        task_file.write_text(task_content, encoding='utf-8')
    
    def _process_generic(self, action_file: Path, content: str):
        """Process a generic action item."""
        # Move to Active_Project for Qwen to process
        dest = self.active_project / action_file.name
        action_file.rename(dest)
        self.logger.info(f'Moved to Active_Project: {action_file.name}')
    
    def complete_item(self, item_file: Path, notes: str = ''):
        """
        Mark an item as complete and move to Done/.
        
        Args:
            item_file: Path to the item file (in Active_Project or Needs_Action)
            notes: Completion notes to append
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Read existing content
        content = item_file.read_text(encoding='utf-8')
        
        # Update status and add completion notes
        if 'status:' in content:
            content = content.replace('status: in_progress', 'status: complete')
            content = content.replace('status: pending', 'status: complete')
        
        # Add completion section
        completion_section = f"""
## Completion
- **Completed**: {datetime.now().isoformat()}
- **Notes**: {notes or 'Task completed successfully'}
"""
        content += completion_section
        
        # Move to Done folder
        done_file = self.done / f'{timestamp}_{item_file.name}'
        done_file.write_text(content, encoding='utf-8')
        
        # Remove original
        if item_file.exists():
            item_file.unlink()
        
        self.stats['items_completed'] += 1
        self.logger.info(f'Completed: {item_file.name} → {done_file.name}')
    
    def update_dashboard(self):
        """Update the Dashboard.md with current status."""
        if not self.dashboard.exists():
            self.logger.warning('Dashboard.md not found, skipping update')
            return
        
        try:
            content = self.dashboard.read_text(encoding='utf-8')
            
            # Count items in various folders
            needs_action_count = len(list(self.needs_action.glob('*.md')))
            active_count = len(list(self.active_project.glob('*.md')))
            done_today = 0
            done_folder = self.done
            if done_folder.exists():
                today_str = datetime.now().strftime('%Y%m%d')
                done_today = len(list(done_folder.glob(f'{today_str}_*.md')))
            
            # Update metrics section (simple string replacement for Bronze tier)
            if 'Pending Tasks |' in content:
                content = content.replace(
                    '| Pending Tasks | 0 |',
                    f'| Pending Tasks | {needs_action_count} |'
                )
            
            if 'Tasks Completed Today |' in content:
                content = content.replace(
                    '| Tasks Completed Today | 0 |',
                    f'| Tasks Completed Today | {done_today} |'
                )
            
            if 'Tasks Completed This Week |' in content:
                week_total = self.stats['items_completed']
                content = content.replace(
                    '| Tasks Completed This Week | 0 |',
                    f'| Tasks Completed This Week | {week_total} |'
                )
            
            # Update last modified
            if 'last_updated:' in content:
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'last_updated:' in line:
                        lines[i] = f'last_updated: {datetime.now().isoformat()}'
                        break
                content = '\n'.join(lines)
            
            self.dashboard.write_text(content, encoding='utf-8')
            self.logger.info('Dashboard updated')
            
        except Exception as e:
            self.logger.error(f'Error updating dashboard: {e}')
    
    def generate_qwen_prompt(self, action_file: Path) -> str:
        """
        Generate a prompt for Qwen Code to process an action file.

        This prompt is designed to be fed to Qwen Code via the Ralph Wiggum
        loop pattern for autonomous processing.

        Args:
            action_file: Path to the action file to process

        Returns:
            Formatted prompt string
        """
        content = action_file.read_text(encoding='utf-8')

        prompt = f"""
I need you to process this action file from my AI Employee vault.

## Action File: {action_file.name}

## Content:
{content}

## Your Task:
1. Read the Company_Handbook.md to understand your rules of engagement
2. Read the Business_Goals.md for current priorities
3. Review this action file and determine what needs to be done
4. If this requires multiple steps, create a Plan.md in the Plans/ folder
5. Execute the work according to the Company_Handbook rules
6. When complete:
   - Move this action file to Done/ with completion notes
   - Update Dashboard.md with the results
   - Log what you did

## Important Rules:
- Check Company_Handbook.md before taking any actions
- For sensitive actions (payments, external communications), create a file in Pending_Approval/ instead of acting directly
- Always be professional in any communications
- Log all your work in the appropriate folders

Please process this now.
"""
        return prompt
    
    def run_processing_cycle(self):
        """Run a single processing cycle."""
        # Check for new items
        new_items = self.check_for_new_items()
        
        if new_items:
            self.logger.info(f'Found {len(new_items)} new item(s) to process')
            
            for item in new_items:
                success = self.process_item(item)
                if success:
                    self.update_dashboard()
                    
                    # Generate and output Qwen prompt for manual processing
                    # In Silver+ tier, this would trigger Qwen automatically
                    prompt = self.generate_qwen_prompt(item)
                    self.logger.info('Qwen prompt generated for manual processing')
        else:
            self.logger.debug('No new items to process')
    
    def run(self, poll_interval: int = 30):
        """
        Main run loop for the orchestrator.
        
        Args:
            poll_interval: Seconds between processing cycles
        """
        self.running = True
        self.stats['start_time'] = datetime.now()
        
        self.logger.info('=' * 60)
        self.logger.info('AI Employee Orchestrator Starting')
        self.logger.info(f'Vault: {self.vault_path}')
        self.logger.info(f'Watchers: {", ".join(self.watcher_types)}')
        self.logger.info('=' * 60)
        
        # Setup and start watchers
        self.setup_watchers()
        self.start_watchers()
        
        # Setup signal handlers for graceful shutdown
        def signal_handler(sig, frame):
            self.logger.info('Shutdown signal received')
            self.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Main processing loop
        try:
            while self.running:
                self.run_processing_cycle()
                time.sleep(poll_interval)
        except Exception as e:
            self.logger.error(f'Fatal error in main loop: {e}')
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Gracefully shutdown all components."""
        self.logger.info('Shutting down orchestrator...')
        self.running = False
        
        # Update dashboard one final time
        self.update_dashboard()
        
        # Log final stats
        runtime = datetime.now() - self.stats['start_time'] if self.stats['start_time'] else None
        self.logger.info('=' * 60)
        self.logger.info('AI Employee Orchestrator Shutdown Complete')
        self.logger.info(f'Runtime: {runtime}')
        self.logger.info(f'Items Processed: {self.stats["items_processed"]}')
        self.logger.info(f'Items Completed: {self.stats["items_completed"]}')
        self.logger.info(f'Errors: {self.stats["errors"]}')
        self.logger.info('=' * 60)


def main():
    """Entry point for running the orchestrator from command line."""
    parser = argparse.ArgumentParser(
        description='AI Employee Orchestrator - coordinates watchers and Qwen processing'
    )
    parser.add_argument(
        'vault_path',
        help='Path to the Obsidian vault root'
    )
    parser.add_argument(
        '--watchers',
        nargs='+',
        default=['fs'],
        help='Watcher types to enable (default: fs)'
    )
    parser.add_argument(
        '--poll-interval',
        type=int,
        default=30,
        help='Seconds between processing cycles (default: 30)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run orchestrator
    orchestrator = Orchestrator(
        vault_path=args.vault_path,
        watcher_types=args.watchers
    )
    
    try:
        orchestrator.run(poll_interval=args.poll_interval)
    except KeyboardInterrupt:
        print('\nShutting down AI Employee Orchestrator...')
        orchestrator.shutdown()


if __name__ == '__main__':
    main()
