#!/usr/bin/env python3
"""
Catch-up check: determines if today's meeting templates were generated.
Called on heartbeat/boot to recover from missed cron runs.
Returns status dict with what needs to be done.
"""

import json
import os
from datetime import datetime, timedelta

from googleapiclient.discovery import build

from config import PROJECTS
from sa_auth import get_credentials, CALENDAR_ID

STATE_FILE = os.path.join(os.path.dirname(__file__), 'last_run.json')


def get_last_run():
    """Get the date of the last successful template generation."""
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE) as f:
        data = json.load(f)
    return data.get('last_generated_for')


def record_run(target_date):
    """Record that templates were successfully generated for a date."""
    with open(STATE_FILE, 'w') as f:
        json.dump({
            'last_generated_for': target_date.isoformat(),
            'generated_at': datetime.now().isoformat(),
        }, f, indent=2)


def check_drive_for_templates(target_date):
    """Check if templates already exist in Drive for the given date."""
    creds = get_credentials()
    drive = build('drive', 'v3', credentials=creds)
    date_str = target_date.strftime('%m.%d.%Y')

    first_project = next((p for p in PROJECTS if p['drive_folder_id']), None)
    if not first_project:
        return False

    query = (
        f"'{first_project['drive_folder_id']}' in parents "
        f"and name contains '{date_str}' "
        f"and trashed=false"
    )
    results = drive.files().list(q=query, fields='files(id, name)').execute()
    return len(results.get('files', [])) > 0


def needs_catchup():
    """Check if we need to generate templates for today's meetings."""
    from calendar_check import get_tomorrows_meetings
    import pytz

    et = pytz.timezone('America/New_York')
    today = datetime.now(et).date()

    last_run = get_last_run()
    if last_run == today.isoformat():
        return False, today, 'Templates already generated for today.'

    # Check if today has meetings by looking at today's calendar (not tomorrow's)
    creds = get_credentials()
    cal = build('calendar', 'v3', credentials=creds)

    today_start = et.localize(datetime.combine(today, datetime.min.time()))
    today_end = et.localize(datetime.combine(today, datetime.max.time()))

    events = cal.events().list(
        calendarId=CALENDAR_ID,
        timeMin=today_start.isoformat(),
        timeMax=today_end.isoformat(),
        maxResults=50,
        singleEvents=True,
        orderBy='startTime',
    ).execute()

    items = events.get('items', [])
    from calendar_check import match_event_to_project
    matched_projects = []
    seen = set()

    for event in items:
        summary = event.get('summary', '') or ''
        project, score = match_event_to_project(summary)
        if project and project['name'] not in seen:
            matched_projects.append(project)
            seen.add(project['name'])

    if not matched_projects:
        return False, today, 'No project meetings today.'

    # Check if templates exist in Drive already
    if check_drive_for_templates(today):
        record_run(today)
        return False, today, 'Templates already exist in Drive for today.'

    return True, today, f'{len(matched_projects)} meetings today but no templates found. Catch-up needed.'


if __name__ == '__main__':
    needed, today, reason = needs_catchup()
    print(f'Date: {today}')
    print(f'Catch-up needed: {needed}')
    print(f'Reason: {reason}')
