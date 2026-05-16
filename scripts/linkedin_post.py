"""
LinkedIn Post Script - Helper to post updates to LinkedIn using Playwright.
This can be called by the AI Employee or via the HITL workflow.
"""

import sys
import time
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright

def post_to_linkedin(content: str, vault_path: str = "./AI_Employee_Vault", media_path: str = None):
    """
    Posts content to LinkedIn using a saved session.
    """
    print(f"Starting LinkedIn post process...")
    user_data_dir = Path(vault_path) / ".linkedin_browser_data"
    
    with sync_playwright() as p:
        # Use a persistent context to stay logged in
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(user_data_dir),
            headless=True
        )
        page = browser.pages[0]
        
        try:
            # Load the feed
            print("Navigating to LinkedIn feed...")
            page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=60000)
            time.sleep(5) # Give it time to load dynamic content
            
            # Check if logged in
            if "login" in page.url or "checkpoint" in page.url:
                print(f"Error: Not logged in or blocked by checkpoint. URL: {page.url}")
                return False

            print("Feed loaded. Looking for 'Start a post'...")
            # Try multiple selectors for the "Start a post" button
            post_triggers = [
                ".share-box-feed-entry__trigger",
                "button.share-box-feed-entry__trigger",
                "text=Start a post",
                "[data-control-name='share_placeholder']"
            ]
            
            trigger_found = False
            for selector in post_triggers:
                try:
                    page.wait_for_selector(selector, timeout=5000)
                    page.click(selector)
                    trigger_found = True
                    print(f"Clicked trigger using: {selector}")
                    break
                except Exception:
                    continue
            
            if not trigger_found:
                print("Error: Could not find 'Start a post' button.")
                return False
            
            # Type content
            print("Editor opened. Typing content...")
            page.wait_for_selector(".ql-editor", timeout=10000)
            page.fill(".ql-editor", content)
            time.sleep(2) # Let it settle
            
            # Click Post
            print("Clicking 'Post'...")
            time.sleep(3) # Ensure button is enabled after typing
            post_buttons = [
                "button.share-actions__post-button",
                ".share-actions__post-button",
                ".artdeco-button--primary",
                "text='Post'",
                "text=Post",
                "button:has-text('Post')"
            ]
            
            post_clicked = False
            for selector in post_buttons:
                try:
                    # Wait for it to be visible and enabled
                    btn = page.wait_for_selector(selector, timeout=3000, state="visible")
                    if btn:
                        page.click(selector)
                        post_clicked = True
                        print(f"Clicked Post using: {selector}")
                        break
                except Exception:
                    continue

            if not post_clicked:
                print("Error: Could not find 'Post' button.")
                return False
            
            # Wait for success toast or feed refresh
            time.sleep(5)
            print("Post successful!")
            return True
            
        except Exception as e:
            print(f"Error during posting: {e}")
            return False
        finally:
            browser.close()

def main():
    parser = argparse.ArgumentParser(description="Post to LinkedIn")
    parser.add_argument("--content", required=True, help="Text content of the post")
    parser.add_argument("--vault", default="./AI_Employee_Vault", help="Path to AI Employee Vault")
    parser.add_argument("--media", help="Path to image/video to upload")
    
    args = parser.parse_args()
    
    success = post_to_linkedin(args.content, args.vault, args.media)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
