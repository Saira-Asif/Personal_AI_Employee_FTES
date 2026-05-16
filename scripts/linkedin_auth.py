"""
LinkedIn Authorization Helper - Launches a headed browser for manual login.
This saves the session to the persistent data directory used by the LinkedIn watcher.
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

def authorize_linkedin(vault_path: str):
    vault = Path(vault_path)
    # Match the path used in linkedin_watcher.py
    user_data_dir = vault / ".linkedin_browser_data"
    
    print("=" * 60)
    print("LinkedIn Authorization Helper")
    print("=" * 60)
    print(f"Data directory: {user_data_dir}")
    print("\nStarting headed browser...")
    print("INSTRUCTIONS:")
    print("1. Log in to your LinkedIn account manually.")
    print("2. Once you see your feed, wait 5 seconds.")
    print("3. Close the browser window. The script will then exit.")
    print("=" * 60)

    try:
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(user_data_dir),
                headless=False,
                slow_mo=500
            )
            page = context.pages[0]
            page.goto("https://www.linkedin.com/login")
            
            print("\nWaiting for login detection...")
            try:
                # Wait for the URL to contain 'feed' which indicates successful login
                page.wait_for_url("**/feed/**", timeout=0)
                print("\nSUCCESS: Login detected!")
                print("Waiting 5 seconds to ensure session data is flushed to disk...")
                time.sleep(5)
                print("READY: You can now close the browser window.")
            except Exception:
                # If they close it before the feed, just continue to close event
                pass
                
            # Wait for the page to be closed manually
            try:
                page.wait_for_event("close", timeout=0)
                print("Browser window closed by user.")
            except Exception:
                pass
                
            context.close()
            print("Session saved successfully.")
            
    except Exception as e:
        print(f"\nError: {e}")
        return False
    
    return True

if __name__ == "__main__":
    vault_arg = "./AI_Employee_Vault"
    if len(sys.argv) > 1:
        vault_arg = sys.argv[1]
    
    success = authorize_linkedin(vault_arg)
    sys.exit(0 if success else 1)
