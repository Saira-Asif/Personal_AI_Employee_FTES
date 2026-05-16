---
name: linkedin-handler
description: Manage LinkedIn interactions, including message replies, lead classification, and automated business posting for sales generation.
---

# LinkedIn Handler Skill

## Overview
This skill enables the AI Employee to manage LinkedIn presence, respond to messages, identify leads, and autonomously post business updates to generate sales.

## When to Use
- When LinkedIn Watcher detects new messages or notifications
- When a task requires posting to LinkedIn for business promotion
- When processing lead-related items from LinkedIn in Needs_Action/
- When the user asks for a summary of LinkedIn activity

## Workflow

### 1. Process New Messages
When a new message is detected by the LinkedIn Watcher:
1. Review the sender's profile and message content
2. Classify the message:
   - **Lead**: Potential customer or business partner (High Priority)
   - **Networking**: General industry contact (Medium Priority)
   - **Spam/Recruiter**: Low priority, usually ignore or archive
3. Create a plan to respond if necessary
4. For Leads: Add details to a central Leads file in the vault

### 2. Automated Business Posting
To generate sales and maintain presence:
1. Consult `Business_Goals.md` for current focus areas (e.g., "AI Consulting", "New Product Launch")
2. Consult `Company_Handbook.md` for brand voice and posting rules
3. Generate post content:
   - **Value-Add**: Tips, insights, or industry news
   - **Promotion**: Specific offers, case studies, or service highlights
   - **Engagement**: Questions or polls
4. Create an approval file in `Pending_Approval/LINKEDIN_POST_<date>.md`
5. After approval, use Browser/LinkedIn MCP to publish the post

### 3. Lead Management
1. Extract contact info and requirements from conversations
2. Update `Business/Leads.md` with new entries
3. Schedule follow-ups via `Tasks/task_tracker.md`

## LinkedIn Post Approval Template
```markdown
---
type: approval_request
action: linkedin_post
scheduled_date: <YYYY-MM-DD>
category: <Promotion/Value-Add/Engagement>
created: <timestamp>
status: pending
---

# LinkedIn Post Approval Request

## Content
<Post text content>

## Media/Links
- <Link or path to image>

## Goal
<What this post aims to achieve, e.g., "Drive traffic to website">

## To Approve
Move this file to approved folder.
```

## Rules
1. Never post to LinkedIn without explicit approval (HITL)
2. Maintain a professional, helpful, and authoritative tone
3. Limit promotional posts to 20% of total volume (80/20 rule)
4. Respond to all non-spam messages within 24 hours
5. Log all posts and significant interactions in `Done/`
6. Never share sensitive business data or internal plans publicly
