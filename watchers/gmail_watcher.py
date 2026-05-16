"""
Gmail Watcher - Monitors Gmail for new unread messages.
"""

import os
import time
import logging
import socket
from pathlib import Path
from datetime import datetime
from typing import List, Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from base_watcher import BaseWatcher

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']

class GmailWatcher(BaseWatcher):
    """
    Monitors Gmail for new unread messages and creates action files.
    """
    
    def __init__(self, vault_path: str, credentials_path: str, token_path: str = 'token.json', check_interval: int = 120):
        """
        Initialize the Gmail watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            credentials_path: Path to the Gmail credentials.json
            token_path: Path to the token.json for persistent auth
            check_interval: Seconds between checks (default: 120)
        """
        super().__init__(vault_path, check_interval)
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.creds = self._authenticate()
        self.service = build('gmail', 'v1', credentials=self.creds)
        self.processed_ids = set()
        self.logger.info("GmailWatcher initialized and authenticated.")

    def _execute_with_retry(self, request, max_retries=5):
        """Executes a Gmail API request with exponential backoff on connection errors."""
        for attempt in range(max_retries):
            try:
                return request.execute()
            except (ConnectionResetError, socket.error, HttpError) as e:
                # WinError 10054 is ConnectionResetError
                if attempt == max_retries - 1:
                    raise
                
                wait_time = (2 ** attempt) + 1
                self.logger.warning(f"Connection error: {e}. Retrying in {wait_time}s... (Attempt {attempt+1}/{max_retries})")
                
                # If it's a connection error, try to rebuild the service
                if isinstance(e, (ConnectionResetError, socket.error)):
                    try:
                        self.service = build('gmail', 'v1', credentials=self.creds)
                    except Exception:
                        pass
                        
                time.sleep(wait_time)

    def _authenticate(self):
        """Authenticates with Gmail API using token.json or credentials.json."""
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(f"Credentials file not found at {self.credentials_path}")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        return creds

    def check_for_updates(self) -> List[Any]:
        """
        Check for new unread messages in Gmail.
        
        Returns:
            List of message summaries
        """
        try:
            # List unread messages in INBOX
            request = self.service.users().messages().list(
                userId='me', q='label:INBOX is:unread'
            )
            results = self._execute_with_retry(request)
            messages = results.get('messages', [])
            
            new_messages = [m for m in messages if m['id'] not in self.processed_ids]
            return new_messages
            
        except Exception as error:
            self.logger.error(f"An error occurred in check_for_updates: {error}")
            return []

    def create_action_file(self, message_summary: Any) -> Path:
        """
        Fetch full message content and create an action file.
        
        Args:
            message_summary: Basic message info with ID
            
        Returns:
            Path to the created action file
        """
        msg_id = message_summary['id']
        try:
            request = self.service.users().messages().get(
                userId='me', id=msg_id, format='full'
            )
            message = self._execute_with_retry(request)
            
            payload = message.get('payload', {})
            headers = payload.get('headers', [])
            
            header_dict = {h['name']: h['value'] for h in headers}
            subject = header_dict.get('Subject', 'No Subject')
            sender = header_dict.get('From', 'Unknown Sender')
            date = header_dict.get('Date', 'Unknown Date')
            
            snippet = message.get('snippet', '')
            
            # Basic content structure
            content = f"""---
type: email
source: gmail
id: {msg_id}
from: {sender}
subject: {subject}
received: {date}
priority: MEDIUM
status: pending
created_at: {datetime.now().isoformat()}
---

# New Email: {subject}

**From:** {sender}
**Date:** {date}

## Snippet
{snippet}

## Instructions
Review this email and decide if action is needed. 
If a reply is required, draft it and place in Pending_Approval.

## Suggested Actions
- [ ] Reply to sender
- [ ] Archive email
- [ ] Create task from email
"""
            
            filename = f"EMAIL_{msg_id}.md"
            filepath = self.needs_action / filename
            
            # Use encoding='utf-8' for safety
            filepath.write_text(content, encoding='utf-8')
            
            # Mark as processed in our local set
            self.processed_ids.add(msg_id)
            
            return filepath
            
        except HttpError as error:
            self.logger.error(f"Error fetching message {msg_id}: {error}")
            raise
