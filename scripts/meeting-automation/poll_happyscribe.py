#!/usr/bin/env python3
"""
Poll HappyScribe for completed transcripts after meetings end.
Run every 5 minutes via crontab (same cycle as send_meeting_reminders.py).

Reads the shared reminders_cache.json to know today's meetings.
For each meeting where now > start + 30 min and now < start + 2 hours,
checks HappyScribe for a completed transcript and triggers the post-meeting workflow.

Cancelled/rescheduled meetings are handled automatically because the reminder
script keeps the cache current.
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from config import PROJECTS
from happyscribe import find_todays_transcripts, match_transcript_to_project
from workflow_postmeeting import process_meeting

CACHE_PATH = os.path.join(SCRIPT_DIR, 'reminders_cache.json')
POLL_STATE_PATH = os.path.join(SCRIPT_DIR, 'poll_state.json')
LOG_PATH = os.path.join(SCRIPT_DIR, 'poll_happyscribe.log')

POLL_START_MINUTES = 30
POLL_TIMEOUT_MINUTES = 120


def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{ts}] {msg}'
    print(line)
    try:
        with open(LOG_PATH, 'a') as f:
            f.write(line + '\n')
    except Exception:
        pass


def parse_start_utc(start_iso):
    import pytz
    start = datetime.fromisoformat(start_iso)
    if start.tzinfo is None:
        start = pytz.timezone('America/New_York').localize(start)
    return start.astimezone(timezone.utc)


def load_meeting_cache():
    if not os.path.exists(CACHE_PATH):
        return []
    with open(CACHE_PATH) as f:
        data = json.load(f)
    return data.get('meetings', [])


def load_poll_state():
    if not os.path.exists(POLL_STATE_PATH):
        return {}
    with open(POLL_STATE_PATH) as f:
        return json.load(f)


def save_poll_state(state):
    with open(POLL_STATE_PATH, 'w') as f:
        json.dump(state, f, indent=2)


def match_meeting_to_project(meeting_name):
    name_lower = meeting_name.lower()
    for project in PROJECTS:
        if project['name'].lower() in name_lower or project['short_name'].lower() in name_lower:
            return project
        if name_lower in project['name'].lower() or name_lower in project['short_name'].lower():
            return project
    return None


def main():
    now_utc = datetime.now(timezone.utc)
    today_str = now_utc.strftime('%Y-%m-%d')

    meetings = load_meeting_cache()
    if not meetings:
        return

    state = load_poll_state()
    # Prune old entries
    state = {k: v for k, v in state.items() if v.get('date') == today_str}

    eligible = []
    for meeting in meetings:
        start_utc = parse_start_utc(meeting['start_iso'])
        minutes_since = (now_utc - start_utc).total_seconds() / 60

        if minutes_since < POLL_START_MINUTES:
            continue
        if minutes_since > POLL_TIMEOUT_MINUTES:
            continue

        state_key = f"{meeting['id']}|{meeting['start_iso']}"
        if state_key in state and state[state_key].get('processed'):
            continue

        project = match_meeting_to_project(meeting['name'])
        if not project:
            continue

        eligible.append((meeting, project, state_key))

    if not eligible:
        return

    # One HappyScribe API call for all eligible meetings
    from datetime import date
    try:
        transcripts = find_todays_transcripts(date.today())
    except Exception as e:
        log(f'HappyScribe API error: {e}')
        return

    if not transcripts:
        names = [m['name'] for m, _, _ in eligible]
        log(f'No transcripts yet for: {", ".join(names)}')
        return

    state_changed = False

    for meeting, project, state_key in eligible:
        matched_transcripts = []
        for t in transcripts:
            t_state = t.get('state', '')
            if t_state != 'automatic_done':
                continue
            match = match_transcript_to_project(t, [project])
            if match:
                matched_transcripts.append(t)

        if not matched_transcripts:
            log(f'No completed transcript yet for: {meeting["name"]}')
            continue

        latest = matched_transcripts[-1]
        transcript_id = latest['id']
        log(f'Found transcript for {meeting["name"]}: {latest.get("name", "?")} (id={transcript_id})')

        try:
            success = process_meeting(project['name'], transcript_id=transcript_id)
            if success:
                log(f'Post-meeting workflow completed for: {project["name"]}')
                state[state_key] = {'date': today_str, 'processed': True, 'transcript_id': transcript_id}
                state_changed = True
            else:
                log(f'Post-meeting workflow failed for: {project["name"]}')
        except Exception as e:
            log(f'Error processing {project["name"]}: {e}')

    if state_changed:
        save_poll_state(state)


if __name__ == '__main__':
    main()
