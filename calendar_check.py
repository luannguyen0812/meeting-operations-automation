#!/usr/bin/env python3
"""
Check Google Calendar for tomorrow's meetings and determine if templates need generation.
Auto-discovers new projects by fuzzy-matching calendar events against known projects.
Alerts when unrecognized meeting events are found.
"""

import json
import os
from datetime import datetime, timedelta
from difflib import SequenceMatcher

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from config import PROJECTS, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

TOKEN_PATH = os.path.join(os.path.dirname(__file__), 'token.json')

SKIP_KEYWORDS = ['lunch', 'break', 'personal', 'dentist', 'doctor', 'holiday', 'pto', 'vacation', 'out of office']


def get_credentials():
    with open(TOKEN_PATH) as f:
        td = json.load(f)
    creds = Credentials(
        token=td['token'],
        refresh_token=td['refresh_token'],
        token_uri=td['token_uri'],
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        td['token'] = creds.token
        with open(TOKEN_PATH, 'w') as f:
            json.dump(td, f, indent=2)
    return creds


def match_event_to_project(event_summary):
    """Fuzzy match a calendar event to a known project. Returns (project, score) or (None, 0)."""
    summary_lower = event_summary.lower()

    for skip in SKIP_KEYWORDS:
        if skip in summary_lower:
            return None, 0

    if 'meeting' not in summary_lower and 'standup' not in summary_lower and 'project' not in summary_lower:
        return None, 0

    best_project = None
    best_score = 0

    for project in PROJECTS:
        for name_variant in [project['name'].lower(), project['short_name'].lower()]:
            words = name_variant.split()
            matching_words = sum(1 for w in words if w in summary_lower and len(w) > 2)
            word_score = matching_words / len(words) if words else 0

            seq_score = SequenceMatcher(None, summary_lower, name_variant).ratio()

            score = max(word_score, seq_score)
            if score > best_score:
                best_score = score
                best_project = project

    if best_score >= 0.4:
        return best_project, best_score
    return None, 0


def get_tomorrows_meetings():
    """Check calendar for tomorrow's meetings. Returns matched projects and unmatched events."""
    creds = get_credentials()
    cal = build('calendar', 'v3', credentials=creds)

    import pytz
    et = pytz.timezone('America/New_York')
    now_et = datetime.now(et)
    tomorrow = (now_et + timedelta(days=1)).date()

    tomorrow_start = et.localize(datetime.combine(tomorrow, datetime.min.time()))
    tomorrow_end = et.localize(datetime.combine(tomorrow, datetime.max.time()))

    events = cal.events().list(
        calendarId='primary',
        timeMin=tomorrow_start.isoformat(),
        timeMax=tomorrow_end.isoformat(),
        maxResults=50,
        singleEvents=True,
        orderBy='startTime',
    ).execute()

    items = events.get('items', [])
    matched_projects = []
    unmatched_meetings = []
    seen_projects = set()

    for event in items:
        summary = event.get('summary', '') or ''
        start = event.get('start', {}).get('dateTime', '')
        time_str = start[11:16] if len(start) > 11 else ''

        project, score = match_event_to_project(summary)

        if project and project['name'] not in seen_projects:
            matched_projects.append(project)
            seen_projects.add(project['name'])
        elif not project and score == 0:
            summary_lower = summary.lower()
            if any(kw in summary_lower for kw in ['meeting', 'standup', 'project', 'sprint', 'review']):
                unmatched_meetings.append({
                    'summary': summary,
                    'time': time_str,
                })

    return matched_projects, unmatched_meetings, tomorrow


def should_generate_templates():
    """Returns (should_generate, projects, unmatched, date)."""
    projects, unmatched, tomorrow = get_tomorrows_meetings()
    return len(projects) > 0, projects, unmatched, tomorrow


if __name__ == '__main__':
    should, projects, unmatched, tomorrow = should_generate_templates()
    day_name = tomorrow.strftime('%A, %B %d, %Y')

    if should:
        print(f'Tomorrow ({day_name}) has {len(projects)} project meetings:')
        for p in projects:
            print(f'  - {p["name"]} ({p["time"]})')
        print('\nTemplates should be generated tonight.')
    else:
        print(f'No project meetings tomorrow ({day_name}). No templates needed.')

    if unmatched:
        print(f'\n⚠ {len(unmatched)} unrecognized meeting event(s):')
        for u in unmatched:
            print(f'  - "{u["summary"]}" at {u["time"]}')
        print('These may be new projects. Add them to config.py to include in automation.')
