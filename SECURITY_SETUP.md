# Harden Your Claude Account Before Connecting Plaud Notes

Your Plaud Notes contain private conversations, meetings, and personal recordings. Before connecting them to Claude, follow this guide to lock down your Claude account so your data stays private.

**Do this BEFORE setting up the Plaud Notes connection.**

---

## Step 1: Turn Off AI Training on Your Data

By default, Claude may use your conversations to improve its models. Turn this off.

- [ ] Go to **[claude.ai/settings](https://claude.ai/settings)**
- [ ] Click **"Data Privacy Controls"** (or go directly to [claude.ai/settings/data-privacy-controls](https://claude.ai/settings/data-privacy-controls))
- [ ] Find the **"Model Improvement"** toggle
- [ ] **Turn it OFF**

**What this does:** With training OFF, your conversations are kept for only 30 days (instead of 5 years) and are never used to train Claude's models. Your meeting transcripts and recordings won't become part of Claude's training data.

---

## Step 2: Review Claude's Memory Settings

Claude's Memory feature remembers things from your past conversations, which can be very useful -- it lets Claude build context about your projects, clients, and preferences over time.

- [ ] Go to **[claude.ai/settings](https://claude.ai/settings)**
- [ ] Click **"Capabilities"** (or **"Memory"** if you see it)
- [ ] Confirm that Memory is **ON** (this is the default and recommended for most users)
- [ ] Review your saved memories periodically by clicking **"Manage Memory"** and remove any specific memories you don't want kept

**Why keep it on:** Memory is what makes Claude your second brain. It lets Claude remember your preferences, project details, and context across conversations. If Claude remembers that Client X prefers a specific tech stack, or that you discussed a deadline last week, that's Memory working for you.

> **Tip:** You can always delete individual memories you don't want stored. Go to Settings > Memory > Manage Memory to review and remove specific items.

---

## Step 3: Use Incognito Chats for Sensitive Sessions

Claude has an "Incognito" mode that creates temporary conversations that are never saved and never used for training.

- [ ] When starting a new conversation about sensitive topics, click the **ghost icon** (next to the "New Chat" button) to start an **Incognito Chat**
- [ ] Use Incognito Chats whenever you're asking Claude to pull up meeting transcripts or sensitive recordings

**What this does:** Incognito conversations are not stored in your chat history, not used for training, and not included in Claude's memory -- regardless of your other settings.

---

## Step 4: Secure Your Claude Login

- [ ] **If you use email login:** Make sure you have a strong, unique password for your Claude account
- [ ] **Better option:** Sign in with **Google** (with Google's 2-Step Verification enabled) or **Apple** (with Apple's two-factor authentication) -- this gives you MFA protection that Claude's email login doesn't offer on its own
- [ ] **Best option (for teams):** If you're on a Claude **Team** or **Enterprise** plan, set up **SSO (Single Sign-On)** through your company's identity provider (Okta, Google Workspace, etc.) which enforces multi-factor authentication

---

## Step 5: Control MCP Tool Permissions

When Claude connects to your Plaud Notes server, it will ask for permission to use each tool. Be intentional about what you approve.

### In Claude Desktop:

- [ ] When Claude asks to use a Plaud Notes tool for the first time, **review what it's doing** before clicking "Allow"
- [ ] **Don't click "Allow always"** unless you fully trust the setup -- approve each time instead, especially at first
- [ ] To disable tools you don't need: click the **"Search and tools"** menu in Claude Desktop and toggle off any Plaud tools you're not currently using

### In Claude Code (CLI):

- [ ] **Don't use `--dangerously-skip-permissions`** -- this bypasses all safety prompts
- [ ] Consider using **`--sandbox`** mode for extra isolation:
  ```
  claude --sandbox
  ```

---

## Step 6: Set Privacy Environment Variables (Claude Code Users)

If you use Claude Code (the CLI tool), add these to your shell profile (`~/.bashrc`, `~/.zshrc`, or similar):

```bash
# Disable non-essential data collection
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
export DISABLE_TELEMETRY=1
export DISABLE_ERROR_REPORTING=1
```

- [ ] Add the lines above to your shell profile
- [ ] Restart your terminal or run `source ~/.bashrc` (or `~/.zshrc`)

**What this does:** Stops Claude Code from sending operational metrics, error reports, and surveys. None of these include your code or file contents, but disabling them is good practice for sensitive work.

---

## Step 7: Never Use /feedback with Sensitive Data

The `/feedback` command in Claude Code sends your **entire conversation transcript** to Anthropic with a **5-year retention period**.

- [ ] **Do not use `/feedback`** in any session where you've loaded Plaud Notes transcripts or meeting content

---

## Step 8: Clean Up After Sensitive Sessions

After you're done working with sensitive Plaud Notes data:

- [ ] **Delete the conversation** from your Claude chat history (click the three dots on the conversation, then "Delete")
- [ ] Deleted conversations are purged from Anthropic's servers within **30 days** and are excluded from any future training

> **Tip:** If you used an Incognito Chat (Step 3), there's nothing to delete -- it was never saved.

---

## Quick Reference: What Goes Where

Understanding what data goes where helps you make informed decisions:

| Data | Where It Lives | Who Can See It |
|------|----------------|----------------|
| Your Plaud recordings (audio files) | Plaud's servers (plaud.ai) | You + Plaud |
| Your Plaud token | Your machine / your cloud host | You only |
| MCP server (this project) | Your machine or your cloud host | You only |
| Tool outputs (transcript text sent to Claude) | Anthropic's servers (30 days with training OFF) | Anthropic's automated systems; human review only if flagged for safety |
| Claude's responses | Anthropic's servers (30 days with training OFF) | Same as above |
| Incognito chat content | Not stored | No one after session ends |

**Key insight:** Your raw audio files never leave Plaud's servers or your MCP server. Only the *text* that the MCP tools return (transcripts, summaries) gets sent to Anthropic's API for Claude to process.

---

## For Teams and Businesses

If your Plaud recordings contain business-sensitive information (client meetings, legal discussions, etc.), consider upgrading to a Claude plan with stronger data protections:

| Feature | Free/Pro/Max | Team | Enterprise |
|---------|-------------|------|------------|
| Opt out of training | Manual toggle | Off by default | Off by default |
| Data retention | 30 days (training off) | 30 days | Custom (min 30 days) |
| SSO with MFA | No (use Google/Apple 2FA) | Yes | Yes |
| Zero Data Retention | No | No | Available by arrangement |
| Admin MCP controls | No | Limited | Full (managed-mcp.json) |
| Custom data policies | No | No | Yes |

For the highest level of protection, Enterprise customers can request **Zero Data Retention (ZDR)** -- Anthropic will not store your inputs or outputs at all.

---

## Checklist Summary

Before connecting Plaud Notes to Claude, confirm you've done all of these:

- [ ] Training toggle is **OFF** ([claude.ai/settings/data-privacy-controls](https://claude.ai/settings/data-privacy-controls))
- [ ] Memory is **ON** and you know how to manage/delete individual memories
- [ ] You know how to start **Incognito Chats** (ghost icon)
- [ ] Your login uses **MFA** (Google 2FA, Apple 2FA, or SSO)
- [ ] You understand MCP tool permissions and won't auto-approve blindly
- [ ] Claude Code privacy env vars are set (if using CLI)
- [ ] You will **never use /feedback** in sensitive sessions
- [ ] You will **delete conversations** with sensitive data when done

**Once all boxes are checked, proceed to the [Setup Guide](https://github.com/jameshenning/PlaudNotes/issues/2) to connect your Plaud Notes.**
