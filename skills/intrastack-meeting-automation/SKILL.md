---
name: "intrastack-meeting-automation"
description: "Reusable patterns and lessons for building automations in Luan's environment: cron, Python, orchestration, credentials."
---

# Automation Patterns (Luan's Environment)

## What This Skill Is For

Use when building any new automation for Luan — not specific to meeting pipelines. Captures the gotchas, architecture patterns, and hard preferences that apply across projects.

---

## Environment Basics

- **Python:** `/usr/bin/python3` (3.9). Do NOT use 3.15 alpha — breaks `cryptography`.
- **Claude CLI:** `/usr/local/bin/claude` — always use the full path when invoking from cron or subprocesses.
- **Credentials:** Store in a `.env.<project>` file in the workspace. Never hardcode, never commit.
- **Workspace:** `~/.openclaw/workspace/` — scripts live under `scripts/<project-name>/`.

---

## Cron Gotchas

Every cron job strips `PATH`. The most common failure mode is a script that works in terminal but silently does nothing in cron.

**Always:**
- Use absolute paths for all binaries: `/usr/bin/python3`, `/usr/local/bin/claude`, `/usr/bin/curl`, etc.
- Test cron scripts by running them with `env -i PATH=/usr/bin:/bin /usr/bin/python3 script.py` to simulate the stripped environment.
- Log cron output to a file (`>> /tmp/<script>.log 2>&1`) during development.

---

## Orchestration Pattern

For multi-step pipelines (fetch → process → send), use a single `workflow_<name>.py` orchestrator that calls smaller, single-responsibility helpers.

```
workflow_<name>.py        ← main entry point, called by cron or manually
├── <source_client>.py    ← API client for data source
├── <process_step>.py     ← transformation/enrichment logic
└── send_<output>.py      ← delivery (email, Telegram, Drive, etc.)
```

Why: makes it easy to rerun just one broken step, and cron only needs one entry point.

---

## Automation Principles (Luan's Preferences)

1. **Fully autonomous** — no manual prompts mid-pipeline. If human input is needed, gate it at setup time, not runtime.
2. **Stateless where possible** — treat local files as temp artifacts; clean up after delivery.
3. **Live data over assumptions** — always query live (calendar, sheet, API) rather than assuming cadence or state from memory.
4. **Last-mile edge cases** — if a trigger can be missed (e.g. same-day additions after nightly cron), document the manual fallback command explicitly. Luan will run it himself.
5. **One cron entry per pipeline** — use polling scripts internally rather than many cron entries.

---

## Claude Integration

- Use OpenClaw's built-in auth — no separate `ANTHROPIC_API_KEY` needed in `.env`.
- When calling `claude` from a subprocess or cron, pass the full path and the prompt via stdin or a temp file.
- For summarization tasks, pass enough grounding context (e.g. full participant roster) to prevent hallucinated names.

---

## Existing Building Blocks

Before writing new code, check `~/.openclaw/workspace/scripts/meeting-automation/` — it already has:
- Google Calendar reader
- HappyScribe API client
- Drive upload/download helpers
- SMTP email sender
- Telegram bot sender
- Roster lookup from Google Sheet

These are reusable as-is for other Intrastack automations.

---

## Lessons Learned

| Mistake | Fix |
|---|---|
| Bare `claude` or `python` in cron | Use full absolute path |
| Polling with wrong API endpoint | Confirm endpoint against actual API docs before coding |
| Wrong MIME type on attachment | Don't rename files to fake the extension — convert properly |
| Fuzzy name matching too strict | Lower threshold (0.5 works); always pass the full expected roster as context |
| Using a local template copy | Re-fetch the source template on each run — don't assume local state persists |
| Separate API key when OpenClaw handles auth | Check if OpenClaw already has auth for the service before adding credentials |
