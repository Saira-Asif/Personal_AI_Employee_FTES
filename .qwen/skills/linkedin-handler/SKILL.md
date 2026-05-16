---
name: linkedin-handler
description: Automate LinkedIn activities including business posting and monitoring interactions via browser automation. Generates leads by sharing business insights and updates.
---

# LinkedIn Handler: Business Development

Promote business goals and generate sales leads via LinkedIn automation.

## When to Use
- **Scheduled Post**: When `scheduler-trigger` initiates a business post.
- **Interaction Monitoring**: To check for likes, comments, or DMs on business posts.
- **Content Creation**: When the user requests to "post... on LinkedIn".

## Workflow: Business Posting

1. **Content**: Generate a post based on `Business_Goals.md` and recent `Done/` tasks.
2. **Consult**: Check `Company_Handbook.md` for branding guidelines.
3. **Approve**: Use `hitl-manager` to save the post draft to `Pending_Approval/`.
4. **Post**: Once approved, use `browser-mcp` to:
   - Navigate to `https://www.linkedin.com`.
   - Click "Start a post".
   - Type the approved content.
   - Click "Post".

## Workflow: Monitoring Leads

1. **Navigate**: Go to the "Notifications" tab or specific post URLs.
2. **Scan**: Identify new comments or connection requests.
3. **Action**: Create `Needs_Action/LINKEDIN_LEAD_<name>.md` for relevant interactions.

## Browser-MCP Quick Reference (LinkedIn)

```bash
# Click 'Start a post'
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_click \
  -p '{"element": "Post button", "ref": "e15"}'

# Type post content (ONLY after approval)
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_type \
  -p '{"element": "Post editor", "ref": "e22", "text": "...", "submit": false}'

# Click 'Post' button
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_click \
  -p '{"element": "Post submit", "ref": "e30"}'
```

## Rules
- **HITL for Posts**: ALL posts MUST be approved via `Pending_Approval/`.
- **Authentic Voice**: Ensure the content reflects the "Digital FTE" identity or the user's voice.
- **Privacy**: Do not capture personal data from LinkedIn beyond what is needed for the lead.
- **Engagement**: Prioritize responding to comments over creating new posts.
