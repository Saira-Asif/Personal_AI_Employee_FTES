"""
LinkedIn Watcher - Monitors LinkedIn for new messages and notifications using Playwright.
"""

import os
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Any

from playwright.sync_api import sync_playwright
from base_watcher import BaseWatcher

class LinkedInWatcher(BaseWatcher):
    """
    Monitors LinkedIn for new messages and connection requests.
    Uses Playwright for browser automation.
    """
    
    def __init__(self, vault_path: str, session_path: str = 'linkedin_session.json', check_interval: int = 300):
        """
        Initialize the LinkedIn watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            session_path: Path to the browser session storage
            check_interval: Seconds between checks (default: 300)
        """
        super().__init__(vault_path, check_interval)
        self.session_path = Path(session_path)
        self.processed_notif_ids = set()
        self.logger.info(f"LinkedInWatcher initialized. Session path: {self.session_path}")

    def check_for_updates(self) -> List[Any]:
        """
        Check for new messages or notifications on LinkedIn.
        
        Returns:
            List of new items
        """
        new_items = []
        
        if not self.session_path.exists():
            self.logger.warning(f"Session file not found at {self.session_path}. Please login manually and save session.")
            return []

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.vault_path / ".linkedin_browser_data"),
                    headless=True
                )
                page = browser.pages[0]
                
                # Load session if exists (though launch_persistent_context handles it if using user_data_dir)
                # But if we have a specific json file, we might need to inject it.
                # For simplicity, we'll rely on the persistent context.
                
                self.logger.info("Navigating to LinkedIn Messaging...")
                page.goto("https://www.linkedin.com/messaging/")
                
                # Check if logged in
                if "login" in page.url:
                    self.logger.error("Not logged in to LinkedIn. Please run manual login script.")
                    browser.close()
                    return []

                # Wait for messaging list
                page.wait_for_selector(".msg-conversations-container", timeout=10000)
                
                # Find unread messages (simple heuristic for now)
                unread_chats = page.query_selector_all(".msg-conversation-card__unread-count")
                
                for chat in unread_chats:
                    # In a real implementation, we would extract sender name and last message
                    # This is a simplified version
                    parent = chat.evaluate_handle("el => el.closest('.msg-conversation-card')")
                    sender = page.evaluate("el => el.querySelector('.msg-conversation-card__participant-names').innerText", parent)
                    snippet = page.evaluate("el => el.querySelector('.msg-conversation-card__message-snippet').innerText", parent)
                    
                    item_id = f"{sender}_{datetime.now().strftime('%Y%m%d%H%M')}"
                    
                    if item_id not in self.processed_notif_ids:
                        new_items.append({
                            'type': 'linkedin_message',
                            'sender': sender,
                            'snippet': snippet,
                            'id': item_id
                        })
                
                browser.close()
                
        except Exception as e:
            self.logger.error(f"Error checking LinkedIn: {e}")
        
        return new_items

    def create_action_file(self, item: Any) -> Path:
        """
        Create an action file for a LinkedIn message.
        """
        item_type = item.get('type')
        sender = item.get('sender')
        snippet = item.get('snippet')
        item_id = item.get('id')
        
        content = f"""---
type: linkedin_message
source: linkedin
sender: {sender}
received: {datetime.now().isoformat()}
status: pending
priority: MEDIUM
---

# New LinkedIn Message from {sender}

## Message Snippet
{snippet}

## Instructions
Review the message and respond if appropriate.
If a post is needed to generate sales, draft it.

## Suggested Actions
- [ ] Reply to {sender}
- [ ] Mark as lead
- [ ] Archive
"""
        
        filename = f"LINKEDIN_{item_id}.md"
        filepath = self.needs_action / filename
        filepath.write_text(content, encoding='utf-8')
        
        self.processed_notif_ids.add(item_id)
        return filepath
