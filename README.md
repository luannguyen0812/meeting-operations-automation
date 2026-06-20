# Meeting Automation Pipeline

A fully automated meeting operations system built in Python. It handles everything around recurring project meetings — from generating agenda templates the night before, to sending Telegram reminders 15 minutes before start, to pulling transcripts after the meeting ends and distributing formatted minutes to the team.

---

## How It Works

```
                        ┌─────────────────────────────────────────┐
                        │           Google Calendar               │
                        └──────────────┬──────────────────────────┘
                                       │
              ┌────────────────────────┼──────────────────────┐
              │                        │                       │
              ▼                        ▼                       ▼
   ┌──────────────────┐   ┌─────────────────────┐  ┌──────────────────────┐
   │  Night-Before    │   │  Meeting Reminder   │  │   Post-Meeting       │
   │  Workflow        │   │  (every 5 min cron) │  │   Workflow           │
   │  (10PM cron)     │   │                     │  │   (manual trigger)   │
   └────────┬─────────┘   └──────────┬──────────┘  └──────────┬───────────┘
            │                        │                         │
            ▼                        ▼                         ▼
   ┌──────────────────┐   ┌─────────────────────┐  ┌──────────────────────┐
   │ Generate .docx   │   │  Telegram Bot       │  │  HappyScribe API     │
   │ agenda templates │   │  "Meeting in 15'"   │  │  (pull transcript)   │
   └────────┬─────────┘   └─────────────────────┘  └──────────┬───────────┘
            │                                                  │
            ▼                                                  ▼
   ┌──────────────────┐                            ┌──────────────────────┐
   │  Google Drive    │                            │  Name correction     │
   │  (upload docs)   │                            │  via team roster     │
   └──────────────────┘                            └──────────┬───────────┘
                                                              │
                                                              ▼
                                                   ┌──────────────────────┐
                                                   │  Format minutes:     │
                                                   │  decisions, actions, │
                                                   │  blockers            │
                                                   └──────────┬───────────┘
                                                              │
                                                              ▼
                                                   ┌──────────────────────┐
                                                   │  Email team via      │
                                                   │  Outlook / Zapier    │
                                                   └──────────────────────┘
```

---

## Features

- **Night-before preparation** — Checks Google Calendar each evening and generates `.docx` agenda templates for tomorrow's project meetings, then uploads them to the correct Google Drive folder per project
- **15-minute Telegram reminders** — Runs every 5 minutes via cron and fires a Telegram message when a meeting is 15 minutes away; also detects and alerts on last-minute cancellations
- **Automated meeting minutes** — After each meeting, pulls the HappyScribe transcript, corrects speaker names against the team roster, extracts decisions / action items / blockers, and emails the formatted minutes to all attendees
- **Multi-project support** — All projects are configured in one place (`config.py`); each project gets its own Drive folder, attendee list, and meeting time
- **Unrecognized meeting detection** — If a calendar event doesn't match any configured project, it alerts so new projects can be added to the automation
- **Catch-up guard** — Tracks last successful run so missed nights (e.g. machine was off) can be detected and handled

---

## Prerequisites

- Python 3.9+
- A Google Cloud project with the **Google Calendar API**, **Google Drive API**, and **Google Sheets API** enabled
- A [HappyScribe](https://www.happyscribe.com) account with API access
- A Telegram bot token (via [@BotFather](https://t.me/botfather))
- A Zapier account with an Outlook "Send Email" action webhook (or SMTP credentials)

---

## Setup

### 1. Clone the repo

```bash
git clone git@github.com:luannguyen0812/meeting-automation.git
cd meeting-automation
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in all values:

| Variable | Where to get it |
|---|---|
| `GOOGLE_CLIENT_ID` | Google Cloud Console → APIs & Services → Credentials |
| `GOOGLE_CLIENT_SECRET` | Same as above |
| `HAPPYSCRIBE_API_KEY` | happyscribe.com → Account → API |
| `ZAPIER_OUTLOOK_WEBHOOK` | Your Zapier webhook URL for Outlook |
| `OUTLOOK_SENDER` | Your Outlook email address |
| `TEAM_SHEET_ID` | Google Drive URL of your roster spreadsheet |

### 4. Authenticate with Google

Run the auth flow once to generate `token.json`:

```bash
python google_auth.py
```

This opens a browser window. Sign in with the Google account that owns the Calendar and Drive you want to use. The token is saved locally and auto-refreshes — you only need to do this once.

### 5. Configure your projects

Edit `config.py` and add an entry to the `PROJECTS` list for each recurring meeting:

```python
PROJECTS = [
    {
        "name": "Project Alpha",           # must match your roster sheet tab name
        "short_name": "Alpha",
        "time": "10:00–10:30 AM EDT",
        "meet_link": "https://meet.google.com/xxx-xxxx-xxx",
        "drive_folder_id": "YOUR_DRIVE_FOLDER_ID",
        "facilitator": "Jane Smith",
        "attendees": ["Jane Smith", "John Doe"],
        "emails": ["jane@company.com", "john@company.com"],
    },
]
```

---

## Usage

### Night-before workflow

Generates agenda templates and uploads to Drive for tomorrow's meetings:

```bash
python workflow_nightbefore.py
```

Force-run even if no meetings are detected:

```bash
python workflow_nightbefore.py --force
```

Run for a specific date:

```bash
python workflow_nightbefore.py 2025-08-15
```

### Post-meeting minutes

Run after a meeting ends to pull the transcript and email the team:

```bash
python workflow_postmeeting.py "Project Alpha"
```

With a specific HappyScribe transcript ID:

```bash
python workflow_postmeeting.py "Project Alpha" transcript_id_here
```

For a past date:

```bash
python workflow_postmeeting.py "Project Alpha" "" 2025-08-14
```

### Meeting reminders

Send a Telegram message 15 minutes before each calendar event:

```bash
python send_meeting_reminders.py
```

This is designed to be run via cron — see the Cron Setup section below.

---

## Cron Setup

Add these entries to your crontab (`crontab -e`):

```cron
# Night-before: generate templates at 10PM every weeknight
0 22 * * 1-5 /usr/bin/python3 /path/to/meeting-automation/workflow_nightbefore.py

# Reminders: check every 5 minutes during work hours
*/5 8-18 * * 1-5 /usr/bin/python3 /path/to/meeting-automation/send_meeting_reminders.py
```

---

## Project Structure

```
meeting-automation/
├── config.py                  # Project list, agenda rows, env var loading
├── google_auth.py             # One-time OAuth flow for Google APIs
├── calendar_check.py          # Check Google Calendar for tomorrow's meetings
├── generate_templates.py      # Create .docx agenda templates
├── drive_upload.py            # Upload generated docs to Google Drive
├── roster.py                  # Download team roster, correct transcript names
├── happyscribe.py             # Pull and match transcripts from HappyScribe API
├── send_email.py              # Send emails via Zapier webhook or SMTP
├── send_meeting_reminders.py  # Telegram reminder bot (runs via cron)
├── catchup_check.py           # Track last successful run, detect missed nights
├── workflow_nightbefore.py    # Orchestrates the night-before pipeline
├── workflow_postmeeting.py    # Orchestrates the post-meeting pipeline
├── requirements.txt           # Python dependencies
└── .env.example               # Environment variable template
```

---

## Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `GOOGLE_CLIENT_ID` | Yes | OAuth 2.0 client ID from Google Cloud |
| `GOOGLE_CLIENT_SECRET` | Yes | OAuth 2.0 client secret from Google Cloud |
| `HAPPYSCRIBE_API_KEY` | Yes | HappyScribe API key for transcript access |
| `ZAPIER_OUTLOOK_WEBHOOK` | Yes | Zapier catch webhook URL for Outlook emails |
| `OUTLOOK_SENDER` | Yes | From address used in outgoing emails |
| `TEAM_SHEET_ID` | Yes | Google Sheets file ID for the team roster |
| `SMTP_HOST` | No | SMTP host if sending email directly instead of Zapier |
| `SMTP_PORT` | No | SMTP port (usually 587) |
| `SMTP_USER` | No | SMTP username |
| `SMTP_PASS` | No | SMTP password |

---

## Security Notes

- Never commit `.env` or `token.json` — both are in `.gitignore`
- `token.json` contains your Google OAuth refresh token; treat it like a password
- The `.env.example` file is safe to commit — it contains no real credentials
