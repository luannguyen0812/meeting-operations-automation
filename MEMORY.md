# MEMORY.md - Long-Term Memory

Curated insights and context. Updated periodically from daily logs.

## Identity

- Agent name: Sparky ⚡
- Human: Luan Nguyen (Luan), timezone America/New_York

## Key Decisions

- [2026-06-17] Set up Obsidian + OpenClaw memory system for persistent context across sessions
- [2026-06-17] Built Intrastack meeting automation (7 projects, template gen + Drive upload + HappyScribe transcripts + SMTP email)
- [2026-06-17] Cron: `meeting-templates-nightly` runs 10PM ET daily, calendar-aware
- [2026-06-22] Post-meeting minutes: fully automated via `poll_happyscribe.py` (cron every 5 min) — detects completed transcripts 30 min–2 hrs after meeting start, no manual trigger needed
- [2026-06-22] Post-meeting output format: Claude summary → filled .docx template → PDF → email (PDF attachment) → upload to project Drive folder → delete local files. Do NOT send raw transcripts.
- [2026-06-22] HappyScribe export bug fixed: was using direct export endpoint, now uses jobs API in `happyscribe.py` — required for auto-polling to work correctly
- [2026-06-22] Claude summarization uses OpenClaw's built-in auth — no separate ANTHROPIC_API_KEY needed in .env.intrastack
- [2026-06-22] Minutes template: always download blank template from Drive, fill it, convert to PDF — never use a local copy (local files deleted on first Drive upload)
- [2026-06-22] Apologies field: detect absentees by cross-referencing HappyScribe transcript participants vs. project roster from Google Sheet
- [2026-06-22] PDF attachment bug fixed: MIME type was wrong (was sending .docx renamed as .pdf); now sends a real PDF
- [2026-06-22] `~/.openclaw` added as additionalDirectory in `~/.claude/settings.json` — eliminates permission prompts for openclaw workspace files
- [2026-06-17] Using Python 3.9 (/usr/bin/python3) for automation scripts — 3.15 alpha breaks cryptography

## Intrastack

- Luan runs 7 projects at Intrastack with meetings every day; Mon & Fri are the two busiest days. ALWAYS check Google Calendar for the actual schedule — never assume cadence from memory.
- Team roster lives in Google Sheet (Excel format on Drive): file ID `1C6tp0z0K6xF50KJMNwqpahHnpH8ajxhB`
- Email via SMTP: mail.intrastack.com, sender luan.nguyen@intrastack.com
- **Always CC stefan.nguyen@intrastack.com** on every minutes email — hardcoded in `send_email.py`
- HappyScribe org ID: 21612080
- Scripts: `~/.openclaw/workspace/scripts/meeting-automation/`
- Credentials: `.env.intrastack` (never commit)
- Name correction: fuzzy match threshold 0.5 (was 0.6); full roster passed to Claude in summarize prompt — prevents garbled names (e.g. Luan → Lorne)
- PATH fix: `workflow_postmeeting.py` uses `/usr/local/bin/claude` (full path) — cron strips PATH
- Luan does not want to manually prompt for minutes; pipeline must be fully autonomous
- Last-minute meetings (added same day): night-before cron already ran, so no agenda/minutes templates exist. Luan will DM Sparky to run them manually via `workflow_nightbefore.py <date>`

## Telegram Meeting Reminders

- Script: `scripts/meeting-automation/send_meeting_reminders.py` — runs every 5 min via crontab
- Sends to Intrastack Communication Channel: `-1003910663531`
- Bot display name changed to something neutral via BotFather (was @LuanAssistanceGuru_bot)
- Messages appear as "Intrastack Communication Channel" (bot added as anonymous admin)
- Reminder format: `<Meeting Name> is starting in 15'\n<meet link>` (Google Meet link appended when available)
- Cancellation format: `⚠️ <Meeting Name> has been cancelled`
- Cache refreshes every 15 min — handles reschedules and cancellations automatically
- Manual overrides: Luan DMs Sparky directly ("cancel X meeting", "push Y to Z time")

## Intern Check-in Bot

- Bot runs on LaunchAgent: `com.intrastack.checkinbot.plist`
- Scripts: `~/.openclaw/workspace/scripts/meeting-automation/` (or similar; check plist for exact path)
- Bot monitors a Telegram group chat for check-in phrases, records attendance in Google Sheets
- ROSTER sheet maps interns' Telegram user IDs → intern details; bot silently drops messages from unregistered users
- Self-registration flow (2026-06-25): interns DM the bot "Hi, my name is [Full Name]" → bot fuzzy-matches against Team Members sheet (75% threshold) → auto-creates ROSTER entry with captured `telegram_user_id`. No manual ID collection needed.
- Meeting-automation reminders and the check-in bot share the same bot token safely: reminders are fire-and-forget HTTP POSTs, only the check-in bot polls. Two pollers on one token = Conflict error, so never do that.

## Personal Telegram Bot (Sparky)

- [2026-06-25] Luan created a separate BotFather bot for interactive AI conversations with Sparky on Telegram
- Token stored at `~/.openclaw/telegram-sparky.token` (never in config as plaintext), referenced via `tokenFile`
- DM-only setup; dmPolicy = "pairing" (send `/start` to pair on first use)
- Completely separate from the intern check-in bot token — different bot, no conflicts

## Habits to Reinforce

- Luan posts credentials in chat — always remind him to delete immediately

## Post-Meeting Pipeline — Cron Auth Failure (2026-06-26)
- ROOT CAUSE of "no minutes sent": post-meeting `ai_summarize()` calls bare `/usr/local/bin/claude --print`. Auth token lives in macOS **login Keychain**, which **cron cannot access** (runs outside GUI session) → "Not logged in" → empty stderr (msg goes to stdout) → every meeting errors at summary step. Worked 6/22; broke after claude CLI updated 6/24 (re-stored creds with Keychain ACL cron can't reach).
- SECOND bug (Jun 25 refactor): PDF export used Drive `export_media` on the uploaded `.docx` → 403 "Export only supports Docs Editors files." Fixed: `export_docx_as_pdf_via_drive()` imports docx as temp Google Doc, exports PDF, deletes temp. Headless, no Word/LibreOffice, cron-safe.
- Also hardened error logging to include stdout (auth errors print there, not stderr).
- DURABLE FIX STILL NEEDED: cron can't reach Keychain for claude. Options: (1) convert poll to LaunchAgent (GUI session = keychain access, same pattern as check-in bot, no API cost) — recommended; (2) ANTHROPIC_API_KEY in subprocess env (file-based, works in cron, separate API cost — Luan previously avoided). Until fixed, Sparky must manually run poll_happyscribe.py from a keychain-having session after each meeting.
