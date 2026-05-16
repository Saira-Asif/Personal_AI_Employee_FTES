"""
Orchestrator - Coordinates watchers and triggers Gemini Code processing.

The Orchestrator:
1. Manages one or more watcher processes
2. Detects when new action files are created in Needs_Action/
3. Triggers Gemini Code to process the items
4. Monitors Approved/ folder and executes actions
5. Monitors completion and moves items to Done/
6. Updates the Dashboard.md with status changes

For Silver Tier: Coordinates FS, Gmail, and LinkedIn watchers with Gemini Code.

Usage:
    python orchestrator.py /path/to/vault

Or with specific watchers:
    python orchestrator.py /path/to/vault --watchers fs gmail linkedin
"""

import sys
import time
import signal
import logging
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))


# Constants
GEMINI_TIMEOUT_SECONDS = 300  # 5 minutes

class Orchestrator:
    """
    Main orchestrator class that coordinates watchers and Gemini processing.
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
        self.approved = self.vault_path / 'Approved'
        self.dashboard = self.vault_path / 'Dashboard.md'
        
        # Ensure directories exist
        for d in [self.needs_action, self.done, self.active_project, self.plans, self.approved]:
            d.mkdir(parents=True, exist_ok=True)
        
        self.watcher_types = watcher_types or ['fs']
        self.watchers = []
        self.running = False
        self.processed_files = set()
        self.executed_approvals = set()
        self.active_processes = {} # Track {pid: {'process': popen_obj, 'start_time': datetime, 'file': filename}}
        
        # Setup logging
        self.logger = logging.getLogger('Orchestrator')
        
        # Track stats
        self.stats = {
            'items_processed': 0,
            'items_completed': 0,
            'actions_executed': 0,
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
        
        if 'gmail' in self.watcher_types:
            from gmail_watcher import GmailWatcher
            self.logger.info('Setting up GmailWatcher...')
            # Using credentials.json from current directory as requested
            gmail_watcher = GmailWatcher(
                vault_path=str(self.vault_path),
                credentials_path='credentials.json'
            )
            self.watchers.append(('gmail', gmail_watcher))
            self.logger.info('GmailWatcher ready')

        if 'linkedin' in self.watcher_types:
            from linkedin_watcher import LinkedInWatcher
            self.logger.info('Setting up LinkedInWatcher...')
            linkedin_watcher = LinkedInWatcher(
                vault_path=str(self.vault_path)
            )
            self.watchers.append(('linkedin', linkedin_watcher))
            self.logger.info('LinkedInWatcher ready')
        
        self.logger.info(f'Initialized {len(self.watchers)} watcher(s)')

    def start_watchers(self):
        """Start all watchers in background threads."""
        import threading
        
        for name, watcher in self.watchers:
            # Note: base_watcher.py uses .run() as the main loop
            thread = threading.Thread(
                target=watcher.run,
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

    def check_for_approvals(self) -> list:
        """
        Check Approved folder for new approval files.
        """
        new_approvals = []
        if not self.approved.exists():
            return new_approvals
        
        for approval_file in self.approved.glob('*.md'):
            if str(approval_file) not in self.executed_approvals:
                new_approvals.append(approval_file)
        
        return new_approvals
    
    def process_item(self, action_file: Path) -> tuple[bool, Path]:
        """
        Process a single action file.

        Args:
            action_file: Path to the action file

        Returns:
            Tuple of (success_bool, current_action_file_path)
        """
        self.logger.info(f'Processing: {action_file.name}')

        try:
            # Read the action file
            content = action_file.read_text(encoding='utf-8')

            current_path = action_file

            # Parse the frontmatter to determine type
            if 'type: file_drop' in content:
                self._process_file_drop(action_file, content)
            elif 'type: email' in content:
                self._process_email(action_file, content)
            elif 'type: linkedin_message' in content:
                self._process_linkedin(action_file, content)
            else:
                current_path = self._process_generic(action_file, content)

            self.stats['items_processed'] += 1
            self.processed_files.add(str(action_file))
            self.processed_files.add(str(current_path))

            return True, current_path

        except Exception as e:
            self.stats['errors'] += 1
            self.logger.error(f'Error processing {action_file.name}: {e}')
            return False, action_file
    def process_approval(self, approval_file: Path) -> bool:
        """
        Execute an approved action.
        """
        self.logger.info(f'Executing approved action: {approval_file.name}')
        
        try:
            content = approval_file.read_text(encoding='utf-8')
            
            # Very simple parser for proof-of-concept
            if 'action: send_email' in content:
                self._execute_send_email(approval_file, content)
            elif 'action: linkedin_post' in content:
                self._execute_linkedin_post(approval_file, content)
            else:
                self.logger.warning(f"Unknown action type in {approval_file.name}")
            
            self.stats['actions_executed'] += 1
            self.executed_approvals.add(str(approval_file))
            
            # Move to Done
            self.complete_item(approval_file, "Action executed successfully")
            return True
            
        except Exception as e:
            self.stats['errors'] += 1
            self.logger.error(f'Error executing action {approval_file.name}: {e}')
            return False

    def _execute_send_email(self, approval_file: Path, content: str):
        """Execute the send_email script."""
        import re
        to_match = re.search(r'to: (.*)', content)
        subject_match = re.search(r'subject: (.*)', content)
        
        # Find body (everything after ## Body)
        body = ""
        if '## Body' in content:
            body = content.split('## Body')[-1].split('##')[0].strip()
        
        if to_match and subject_match:
            to = to_match.group(1).strip()
            subject = subject_match.group(1).strip()
            
            self.logger.info(f"Sending email to {to}...")
            
            # Call our script
            scripts_dir = Path(__file__).parent.parent / 'scripts'
            cmd = [
                sys.executable, 
                str(scripts_dir / 'send_email.py'),
                '--to', to,
                '--subject', subject,
                '--body', body
            ]
            
            # Use a timeout for action scripts
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                self.logger.info(f"Email sent successfully.")
            else:
                self.logger.error(f"Failed to send email: {result.stderr}")
                raise Exception(f"Script failed: {result.stderr}")

    def _execute_linkedin_post(self, approval_file: Path, content: str):
        """Execute the linkedin_post script."""
        # Find post content (everything after ## Content)
        post_text = ""
        if '## Content' in content:
            post_text = content.split('## Content')[-1].split('##')[0].strip()
        
        if post_text:
            self.logger.info(f"Posting to LinkedIn...")
            
            # Call our script
            scripts_dir = Path(__file__).parent.parent / 'scripts'
            cmd = [
                sys.executable, 
                str(scripts_dir / 'linkedin_post.py'),
                '--content', post_text
            ]
            
            # Use a longer timeout for LinkedIn as it uses Playwright
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                self.logger.info(f"LinkedIn post successful.")
            else:
                self.logger.error(f"Failed to post to LinkedIn: {result.stderr}")
                raise Exception(f"Script failed: {result.stderr}")

    def _process_file_drop(self, action_file: Path, content: str):
        """Process a file drop action item."""
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

    def _process_linkedin(self, action_file: Path, content: str):
        """Process a LinkedIn message action item."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        task_content = f"""---
type: task
created: {datetime.now().isoformat()}
status: pending
priority: HIGH
source: {action_file.name}
---

# LinkedIn Message Review Required

## Details
New message detected on LinkedIn.

## Required Actions
- [ ] Review LinkedIn message
- [ ] Respond to sender
- [ ] If lead, add to CRM/Leads file
- [ ] Draft a sales post if this message suggests a new opportunity

"""
        task_file = self.needs_action / f'TASK_linkedin_review_{timestamp}.md'
        task_file.write_text(task_content, encoding='utf-8')

    def _process_generic(self, action_file: Path, content: str) -> Path:
        """Process a generic action item."""
        # Move to Active_Project for Gemini to process
        dest = self.active_project / action_file.name
        action_file.rename(dest)
        self.logger.info(f'Moved to Active_Project: {action_file.name}')
        return dest
    
    def complete_item(self, item_file: Path, notes: str = ''):
        """
        Mark an item as complete and move to Done/.
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Read existing content if possible
        if not item_file.exists():
             self.logger.warning(f"File {item_file} not found for completion.")
             return

        content = item_file.read_text(encoding='utf-8')
        
        # Update status and add completion notes
        content = content.replace('status: pending', 'status: complete')
        content = content.replace('status: in_progress', 'status: complete')
        
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
            pending_approval_count = len(list(self.vault_path.glob('Pending_Approval/*.md')))
            
            done_today = 0
            done_folder = self.done
            if done_folder.exists():
                today_str = datetime.now().strftime('%Y%m%d')
                done_today = len(list(done_folder.glob(f'{today_str}_*.md')))
            
            # Update metrics section
            import re
            content = re.sub(r'\| Pending Tasks \| \d+ \|', f'| Pending Tasks | {needs_action_count} |', content)
            content = re.sub(r'\| Tasks Completed Today \| \d+ \|', f'| Tasks Completed Today | {done_today} |', content)
            content = re.sub(r'\| Pending Approvals \| \d+ \|', f'| Pending Approvals | {pending_approval_count} |', content)
            
            # Update last modified
            if 'last_updated:' in content:
                content = re.sub(r'last_updated: .*', f'last_updated: {datetime.now().isoformat()}', content)
            
            self.dashboard.write_text(content, encoding='utf-8')
            self.logger.info('Dashboard updated')
            
        except Exception as e:
            self.logger.error(f'Error updating dashboard: {e}')
    
    def generate_gemini_prompt(self, action_file: Path) -> str:
        """
        Generate a prompt for Gemini Code to process an action file.
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
        # 1. Check for new items in Needs_Action
        new_items = self.check_for_new_items()
        for item in new_items:
            success, current_path = self.process_item(item)
            if success:
                self.update_dashboard()
                # Automatically trigger the Brain to process the new task
                self._trigger_gemini_brain(current_path)
        
        # 2. Check for new items in Approved
        new_approvals = self.check_for_approvals()
        for approval in new_approvals:
            success = self.process_approval(approval)
            if success:
                self.update_dashboard()
        
        # 3. Monitor background processes
        self._monitor_processes()

    def _trigger_gemini_brain(self, action_file: Path):
        """
        Trigger the Gemini CLI to process a specific task.
        Runs in the background to avoid blocking the orchestrator.
        """
        self.logger.info(f"Triggering Gemini Brain for: {action_file.name}")
        
        prompt = self.generate_gemini_prompt(action_file)
        
        try:
            # Create a unique log file for this Gemini run for debugging
            log_dir = self.vault_path / "Logs"
            log_dir.mkdir(exist_ok=True)
            log_file = log_dir / f"gemini_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            
            self.logger.info(f"Handoff to Gemini initiated. Logs: {log_file.name}")
            
            # Launch Gemini in background
            # On Windows, we use CREATE_NEW_PROCESS_GROUP to allow killing the group later if needed
            with open(log_file, "w") as f:
                process = subprocess.Popen(
                    ["gemini", prompt],
                    stdout=f,
                    stderr=f,
                    shell=True,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
                )
            
            # Track the process
            self.active_processes[process.pid] = {
                'process': process,
                'start_time': datetime.now(),
                'file': action_file.name,
                'log_file': log_file
            }
            
            self.logger.info(f"Gemini process started with PID: {process.pid}")
            
        except Exception as e:
            self.logger.error(f"Failed to trigger Gemini brain: {e}")

    def _monitor_processes(self):
        """
        Monitor background Gemini processes for completion or timeouts.
        """
        if not self.active_processes:
            return

        completed_pids = []
        
        for pid, info in self.active_processes.items():
            process = info['process']
            start_time = info['start_time']
            filename = info['file']
            
            # Check if process is still running
            exit_code = process.poll()
            
            if exit_code is not None:
                self.logger.info(f"Gemini process {pid} ({filename}) finished with code {exit_code}")
                completed_pids.append(pid)
                continue
                
            # Check for timeout
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed > GEMINI_TIMEOUT_SECONDS:
                self.logger.warning(f"Gemini process {pid} ({filename}) timed out after {elapsed}s. Terminating...")
                try:
                    if sys.platform == 'win32':
                        # On Windows, taskkill /F /T kills the process group
                        subprocess.run(['taskkill', '/F', '/T', '/PID', str(pid)], 
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    else:
                        process.terminate()
                        time.sleep(2)
                        if process.poll() is None:
                            process.kill()
                except Exception as e:
                    self.logger.error(f"Error terminating process {pid}: {e}")
                
                completed_pids.append(pid)

        # Remove completed/terminated processes
        for pid in completed_pids:
            del self.active_processes[pid]

    def run(self, poll_interval: int = 30):
        """
        Main run loop for the orchestrator.
        """
        self.running = True
        self.stats['start_time'] = datetime.now()
        
        self.logger.info('=' * 60)
        self.logger.info('AI Employee Orchestrator Starting (Gemini Edition)')
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
        self.logger.info(f'Actions Executed: {self.stats["actions_executed"]}')
        self.logger.info(f'Errors: {self.stats["errors"]}')
        self.logger.info('=' * 60)


def main():
    """Entry point for running the orchestrator from command line."""
    parser = argparse.ArgumentParser(
        description='AI Employee Orchestrator - coordinates watchers and Gemini processing'
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
