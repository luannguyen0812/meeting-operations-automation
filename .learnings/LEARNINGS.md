# Learnings

Corrections, insights, and knowledge gaps captured during development.

**Categories**: correction | insight | knowledge_gap | best_practice

---

## [LRN-20260624-001] correction

**Logged**: 2026-06-24T14:00:00Z
**Priority**: high
**Status**: resolved
**Area**: infra

### Summary
Cron strips PATH — bare binary names silently fail

### Details
Scripts that ran fine in terminal did nothing in cron. Root cause: cron sets a minimal PATH that doesn't include `/usr/local/bin`. Any call to `claude`, `python3`, or other non-standard binaries needs the full absolute path.

### Suggested Action
Always use `/usr/bin/python3` and `/usr/local/bin/claude` in cron-invoked scripts. Test with `env -i PATH=/usr/bin:/bin /usr/bin/python3 script.py` to simulate.

### Metadata
- Source: conversation
- Related Files: scripts/meeting-automation/workflow_postmeeting.py
- Tags: cron, path, python, claude-cli
- Pattern-Key: infra.cron_path_stripping
- Recurrence-Count: 1

---

## [LRN-20260624-002] correction

**Logged**: 2026-06-24T14:00:00Z
**Priority**: high
**Status**: resolved
**Area**: backend

### Summary
HappyScribe: direct export endpoint doesn't work for polling — must use jobs API

### Details
Initial implementation used HappyScribe's direct export endpoint. This worked for one-shot fetches but broke the auto-polling flow. The jobs API is required to check transcript status and retrieve output for the polling pipeline.

### Suggested Action
When integrating any transcript/async service, use the jobs/status API, not the one-shot export endpoint.

### Metadata
- Source: conversation
- Related Files: scripts/meeting-automation/happyscribe.py
- Tags: happyscribe, api, polling
- Pattern-Key: backend.async_api_endpoint_selection

---

## [LRN-20260624-003] correction

**Logged**: 2026-06-24T14:00:00Z
**Priority**: high
**Status**: resolved
**Area**: backend

### Summary
Renaming a .docx to .pdf doesn't make it a PDF — MIME type mismatch breaks email clients

### Details
Email attachment was being sent with a `.pdf` extension but the file was actually a `.docx`. Email clients either refused to open it or opened it as garbage. Must convert properly (e.g. via LibreOffice or python-docx2pdf).

### Suggested Action
Always convert, never rename. Verify MIME type matches actual file format before attaching.

### Metadata
- Source: conversation
- Related Files: scripts/meeting-automation/send_email.py
- Tags: email, pdf, mime, docx
- Pattern-Key: backend.file_format_conversion

---

## [LRN-20260624-004] correction

**Logged**: 2026-06-24T14:00:00Z
**Priority**: medium
**Status**: resolved
**Area**: backend

### Summary
Fuzzy name matching too strict caused garbled names in Claude summarization output

### Details
Fuzzy match threshold of 0.6 was too aggressive — real names like "Luan" were matching incorrectly (e.g. output "Lorne"). Two fixes: lower threshold to 0.5, and pass the full expected roster to Claude in the summarization prompt so it has ground truth to anchor against.

### Suggested Action
For any NLP/summarization task involving proper nouns, always pass a reference list as context. Don't rely solely on fuzzy matching.

### Metadata
- Source: conversation
- Related Files: scripts/meeting-automation/workflow_postmeeting.py
- Tags: claude, summarization, fuzzy-matching, names
- Pattern-Key: backend.llm_name_grounding

---

## [LRN-20260624-005] correction

**Logged**: 2026-06-24T14:00:00Z
**Priority**: medium
**Status**: resolved
**Area**: infra

### Summary
Adding a separate ANTHROPIC_API_KEY is unnecessary — OpenClaw handles Claude auth

### Details
Initially added ANTHROPIC_API_KEY to .env.intrastack. Not needed. OpenClaw's built-in auth handles all Claude CLI calls. Adding a redundant key can cause confusion about which credential is active.

### Suggested Action
Before adding API credentials for any service, check if OpenClaw already provides auth for it.

### Metadata
- Source: conversation
- Related Files: .env.intrastack
- Tags: auth, claude, openclaw, credentials
- Pattern-Key: infra.openclaw_auth_check

---

## [LRN-20260624-006] correction

**Logged**: 2026-06-24T14:00:00Z
**Priority**: medium
**Status**: resolved
**Area**: infra

### Summary
Local template copy gets deleted on first Drive upload — always re-fetch from Drive

### Details
Post-meeting pipeline deletes local files after Drive upload. On the next run, code tried to use a local template copy that no longer existed. Fix: always download the blank template fresh from Drive at the start of each run.

### Suggested Action
In any pipeline that cleans up local files, treat every run as stateless — re-fetch all inputs from their source at runtime.

### Metadata
- Source: conversation
- Related Files: scripts/meeting-automation/workflow_postmeeting.py
- Tags: drive, templates, stateless, local-files
- Pattern-Key: infra.stateless_pipeline_inputs

---
