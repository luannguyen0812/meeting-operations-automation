#!/usr/bin/env python3
"""Service account credentials for meeting automation — no OAuth tokens, no expiry."""

import os
from google.oauth2 import service_account

_INTERN_BOT_SA = os.path.expanduser(
    "~/Claude/Projects/Team announcement — Daily check‑ins and Weekly Attendance Reporting"
    "/intern_checkin_bot/secrets/service-account.json"
)

DRIVE_SCOPES = [
    "https://www.googleapis.com/auth/drive",
]
CALENDAR_SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
]
ALL_SCOPES = DRIVE_SCOPES + CALENDAR_SCOPES + [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]

CALENDAR_ID = "luan.nguyen@intrastack.com"


def get_credentials(scopes=None):
    """Return service account credentials. Scopes default to ALL_SCOPES."""
    if scopes is None:
        scopes = ALL_SCOPES
    sa_path = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON") or _INTERN_BOT_SA
    return service_account.Credentials.from_service_account_file(sa_path, scopes=scopes)
