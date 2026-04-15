"""
Base Watcher - Abstract foundation for all AI Employee watchers.

All watchers follow this pattern:
1. Continuously monitor a data source (email, files, messages, etc.)
2. Detect new/changed items that need processing
3. Create action files in the Needs_Action folder for Qwen Code to process
4. Log all activity for audit purposes

Usage:
    Inherit from BaseWatcher and implement the two abstract methods:
    - check_for_updates(): Return list of new items to process
    - create_action_file(item): Create .md file in Needs_Action folder
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class BaseWatcher(ABC):
    """
    Abstract base class for all AI Employee watchers.
    
    Watchers run continuously in the background, monitoring various
    inputs and creating actionable .md files for Qwen Code to process.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.inbox = self.vault_path / 'Inbox'
        self.check_interval = check_interval
        self.running = False
        self.items_processed = 0
        self.errors_encountered = 0
        
        # Ensure required directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.inbox.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(self.__class__.__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    @abstractmethod
    def check_for_updates(self) -> list:
        """
        Check for new items that need processing.
        
        Returns:
            List of new items (format depends on watcher type)
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item: Any) -> Path:
        """
        Create an action file in the Needs_Action folder.
        
        Args:
            item: Item from check_for_updates() to process
            
        Returns:
            Path to the created action file
        """
        pass
    
    def run(self):
        """
        Main loop - runs continuously until stopped.
        
        This method:
        1. Checks for new items
        2. Creates action files for each
        3. Logs any errors
        4. Sleeps for the check interval
        """
        self.running = True
        self.logger.info(f'Starting {self.__class__.__name__}')
        
        try:
            while self.running:
                try:
                    items = self.check_for_updates()
                    for item in items:
                        try:
                            action_file = self.create_action_file(item)
                            self.items_processed += 1
                            self.logger.info(f'Created action file: {action_file.name}')
                        except Exception as e:
                            self.errors_encountered += 1
                            self.logger.error(f'Error creating action file: {e}')
                    
                except Exception as e:
                    self.errors_encountered += 1
                    self.logger.error(f'Error in check cycle: {e}')
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info(f'{self.__class__.__name__} stopped by user')
        finally:
            self.running = False
            self.logger.info(
                f'{self.__class__.__name__} shutdown. '
                f'Processed: {self.items_processed}, '
                f'Errors: {self.errors_encountered}'
            )
    
    def stop(self):
        """Signal the watcher to stop."""
        self.running = False
    
    def get_status(self) -> dict:
        """
        Get current status of the watcher.
        
        Returns:
            Dictionary with watcher status information
        """
        return {
            'name': self.__class__.__name__,
            'running': self.running,
            'vault_path': str(self.vault_path),
            'check_interval': self.check_interval,
            'items_processed': self.items_processed,
            'errors_encountered': self.errors_encountered,
        }
