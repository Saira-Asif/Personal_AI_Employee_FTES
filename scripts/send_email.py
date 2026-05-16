"""
Email Send Script - Helper to send emails via Gmail API.
"""

import os
import sys
import argparse
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
import base64

def send_email(to, subject, body, token_path='token.json'):
    """Sends an email using Gmail API."""
    if not os.path.exists(token_path):
        print(f"Error: token.json not found at {token_path}")
        return False

    creds = Credentials.from_authorized_user_file(token_path)
    service = build('gmail', 'v1', credentials=creds)

    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject

    # Encode to base64
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    
    try:
        sent_msg = service.users().messages().send(userId='me', body={'raw': raw}).execute()
        print(f"Email sent successfully! Message ID: {sent_msg['id']}")
        return True
    except HttpError as error:
        print(f"An error occurred: {error}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Send Email via Gmail")
    parser.add_argument("--to", required=True)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--body", required=True)
    parser.add_argument("--token", default="token.json")
    
    args = parser.parse_args()
    
    success = send_email(args.to, args.subject, args.body, args.token)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
