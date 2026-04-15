"""
File System Watcher - Monitors a drop folder for new files.

This watcher monitors a specified directory for new files being created or
moved into it. When a new file is detected, it:
1. Creates an action file in the Needs_Action folder
2. Optionally copies/moves the file to the Inbox folder
3. Logs the activity

This is the simplest watcher to get started with - just drop files into the
watched folder and the AI Employee will pick them up for processing.

Usage:
    python filesystem_watcher.py /path/to/vault /path/to/watch/folder

Or with defaults (watches the vault's Inbox folder):
    python filesystem_watcher.py /path/to/vault
"""

import sys
import time
import logging
from pathlib import Path
from datetime import datetime

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from base_watcher import BaseWatcher


class DropFolderHandler(FileSystemEventHandler):
    """Handles file system events and creates action files."""
    
    def __init__(self, vault_path: Path, processed_ids: set = None):
        """
        Initialize the handler.
        
        Args:
            vault_path: Path to the Obsidian vault root
            processed_ids: Set of already-processed file paths to avoid duplicates
        """
        self.vault_path = vault_path
        self.needs_action = vault_path / 'Needs_Action'
        self.inbox = vault_path / 'Inbox'
        self.processed_ids = processed_ids or set()
        self.logger = logging.getLogger('DropFolderHandler')
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.inbox.mkdir(parents=True, exist_ok=True)
    
    def on_created(self, event):
        """Handle new file creation."""
        if event.is_directory:
            return
        
        self._handle_new_file(Path(event.src_path))
    
    def on_modified(self, event):
        """Handle file modifications (treat as new if not yet processed)."""
        if event.is_directory:
            return
        
        src_path = Path(event.src_path)
        if str(src_path) not in self.processed_ids:
            self._handle_new_file(src_path)
    
    def on_moved(self, event):
        """Handle file moves into the watched directory."""
        if event.is_directory:
            return
        
        dest_path = Path(event.dest_path)
        if str(dest_path) not in self.processed_ids:
            self._handle_new_file(dest_path)
    
    def _handle_new_file(self, source: Path):
        """
        Process a newly detected file.
        
        Args:
            source: Path to the new file
        """
        # Skip hidden files and temporary files
        if source.name.startswith('.') or source.name.startswith('~'):
            return
        
        # Skip if already processed
        if str(source) in self.processed_ids:
            return
        
        self.logger.info(f'New file detected: {source.name}')
        
        try:
            # Create action file in Needs_Action
            action_file = self._create_action_file(source)
            self.processed_ids.add(str(source))
            
            self.logger.info(f'Action file created: {action_file.name}')
            
        except Exception as e:
            self.logger.error(f'Error processing file {source.name}: {e}')
    
    def _create_action_file(self, source: Path) -> Path:
        """
        Create a markdown action file for the detected file.
        
        Args:
            source: Path to the original file
            
        Returns:
            Path to the created action file
        """
        # Get file info
        file_stat = source.stat()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_extension = source.suffix.lower()
        
        # Determine file type based on extension
        file_type_map = {
            '.txt': 'text',
            '.md': 'markdown',
            '.pdf': 'document',
            '.doc': 'document',
            '.docx': 'document',
            '.csv': 'spreadsheet',
            '.xls': 'spreadsheet',
            '.xlsx': 'spreadsheet',
            '.png': 'image',
            '.jpg': 'image',
            '.jpeg': 'image',
            '.gif': 'image',
        }
        file_type = file_type_map.get(file_extension, 'unknown')
        
        # Create the action file content
        content = f"""---
type: file_drop
source: filesystem_watcher
original_name: {source.name}
original_path: {source}
file_type: {file_type}
file_extension: {file_extension}
file_size: {file_stat.st_size} bytes
created: {datetime.now().isoformat()}
status: pending
---

# File Dropped for Processing

## File Information
- **Name**: {source.name}
- **Type**: {file_type}
- **Size**: {file_stat.st_size} bytes ({file_stat.st_size / 1024:.1f} KB)
- **Last Modified**: {datetime.fromtimestamp(file_stat.st_mtime).isoformat()}

## Location
- **Dropped in**: {source.parent}
- **Absolute Path**: {source.absolute()}

## Suggested Actions
- [ ] Review file contents
- [ ] Categorize and tag appropriately
- [ ] Determine required processing
- [ ] Move to appropriate folder when done

## Notes
_Add any processing notes here_

"""
        
        # Create unique filename to avoid conflicts
        safe_name = source.stem.replace(' ', '_')[:50]
        action_filename = f'FILE_{timestamp}_{safe_name}.md'
        action_path = self.needs_action / action_filename
        
        # Write the action file
        action_path.write_text(content, encoding='utf-8')
        
        return action_path


class FileSystemWatcher:
    """
    File System Watcher - monitors a directory for new files.
    
    This wraps the DropFolderHandler with a watchdog Observer to provide
    continuous monitoring.
    """
    
    def __init__(self, vault_path: str, watch_path: str = None, 
                 check_interval: int = 5):
        """
        Initialize the file system watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            watch_path: Path to the directory to watch (default: vault's Inbox)
            check_interval: Not used with watchdog (event-driven), kept for API compatibility
        """
        self.vault_path = Path(vault_path)
        self.watch_path = Path(watch_path) if watch_path else self.vault_path / 'Inbox'
        self.processed_ids = set()
        self.logger = logging.getLogger('FileSystemWatcher')
        
        # Ensure watch directory exists
        self.watch_path.mkdir(parents=True, exist_ok=True)
        
        # Setup the handler and observer
        self.handler = DropFolderHandler(self.vault_path, self.processed_ids)
        self.observer = Observer()
        self.observer.schedule(
            self.handler,
            str(self.watch_path),
            recursive=False
        )
        
        self.running = False
        self.items_processed = 0
        self.errors_encountered = 0
    
    def start(self):
        """Start watching the directory."""
        self.running = True
        self.logger.info(
            f'Starting FileSystemWatcher'
        )
        self.logger.info(f'Watching: {self.watch_path}')
        self.logger.info(f'Vault: {self.vault_path}')
        self.observer.start()
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop watching."""
        self.running = False
        self.observer.stop()
        self.observer.join()
        self.logger.info('FileSystemWatcher stopped')
        self.logger.info(
            f'Processed: {self.handler.processed_ids.__len__()} files'
        )
    
    def get_status(self) -> dict:
        """Get current status of the watcher."""
        return {
            'name': 'FileSystemWatcher',
            'running': self.running,
            'watch_path': str(self.watch_path),
            'vault_path': str(self.vault_path),
            'files_processed': len(self.processed_ids),
        }


def main():
    """Entry point for running the watcher from command line."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Monitor a directory for new files and create action items.'
    )
    parser.add_argument(
        'vault_path',
        help='Path to the Obsidian vault root'
    )
    parser.add_argument(
        '--watch-path',
        help='Path to the directory to watch (default: vault/Inbox)'
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
    
    # Create and start the watcher
    watcher = FileSystemWatcher(
        vault_path=args.vault_path,
        watch_path=args.watch_path
    )
    
    try:
        watcher.start()
    except KeyboardInterrupt:
        print('\nShutting down FileSystemWatcher...')
        watcher.stop()


if __name__ == '__main__':
    main()
