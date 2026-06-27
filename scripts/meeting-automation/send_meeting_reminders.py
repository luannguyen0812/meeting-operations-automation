#!/usr/bin/env python3
"""
Send Telegram meeting reminders 15 minutes before calendar events.
Run every 5 minutes via crontab. Caches calendar data for 15 minutes to catch last-minute reschedules.
"""

import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timedelta, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from googleapiclient.discovery import build
from sa_auth import get_credentials as _sa_get_credentials, CALENDAR_ID

CACHE_PATH = os.path.join(SCRIPT_DIR, 'reminders_cache.json')
SENT_PATH = os.path.join(SCRIPT_DIR, 'sent_reminders.json')
OPENCLAW_CONFIG = os.path.expanduser('~/.openclaw/openclaw.json')
TELEGRAM_CHANNEL = '-1003910663531'
CACHE_TTL_MINUTES = 15

SKIP_KEYWORDS = ['lunch', 'break', 'personal', 'dentist', 'doctor', 'holiday', 'pto', 'vacation', 'out of office']


def get_bot_token():
    # Try env var first (set when running under OpenClaw)
    if os.environ.get('TELEGRAM_BOT_TOKEN'):
        return os.environ['TELEGRAM_BOT_TOKEN']
    # Load from OpenClaw .env file for standalone cron runs
    env_path = os.path.expanduser('~/.openclaw/.env')
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith('TELEGRAM_BOT_TOKEN='):
                    return line.split('=', 1)[1].strip()
    # Fall back to raw config value (may be an env var ref)
    with open(OPENCLAW_CONFIG) as f:
        cfg = json.load(f)
    token = cfg['channels']['telegram']['botToken']
    if token.startswith('${') and token.endswith('}'):
        var = token[2:-1]
        return os.environ.get(var, '')
    return token


def get_google_credentials():
    return _sa_get_credentials()


def fetch_todays_meetings():
    """Fetch all timed events from today's Google Calendar."""
    import pytz
    et = pytz.timezone('America/New_York')
    now_et = datetime.now(et)
    today = now_et.date()

    day_start = et.localize(datetime.combine(today, datetime.min.time()))
    day_end = et.localize(datetime.combine(today, datetime.max.time()))

    creds = get_google_credentials()
    cal = build('calendar', 'v3', credentials=creds)
    events = cal.events().list(
        calendarId=CALENDAR_ID,
        timeMin=day_start.isoformat(),
        timeMax=day_end.isoformat(),
        maxResults=50,
        singleEvents=True,
        orderBy='startTime',
    ).execute()

    meetings = []
    for event in events.get('items', []):
        start_dt = event.get('start', {}).get('dateTime')
        if not start_dt:
            continue  # skip all-day events

        summary = event.get('summary', '') or 'Meeting'
        summary_lower = summary.lower()
        if any(kw in summary_lower for kw in SKIP_KEYWORDS):
            continue

        # Prefer hangoutLink; fall back to conferenceData video entry point
        meet_link = event.get('hangoutLink', '')
        if not meet_link:
            for ep in (event.get('conferenceData') or {}).get('entryPoints', []):
                if ep.get('entryPointType') == 'video':
                    meet_link = ep.get('uri', '')
                    break

        meetings.append({
            'id': event.get('id', ''),
            'name': summary,
            'start_iso': start_dt,
            'meet_link': meet_link,
        })

    return meetings


def load_cache():
    if not os.path.exists(CACHE_PATH):
        return None, None
    with open(CACHE_PATH) as f:
        data = json.load(f)
    cached_at = datetime.fromisoformat(data['cached_at'])
    if cached_at.tzinfo is None:
        cached_at = cached_at.replace(tzinfo=timezone.utc)
    return data['meetings'], cached_at


def save_cache(meetings):
    with open(CACHE_PATH, 'w') as f:
        json.dump({
            'cached_at': datetime.now(timezone.utc).isoformat(),
            'meetings': meetings,
        }, f, indent=2)


def load_sent():
    if not os.path.exists(SENT_PATH):
        return {}
    with open(SENT_PATH) as f:
        return json.load(f)


def save_sent(sent):
    with open(SENT_PATH, 'w') as f:
        json.dump(sent, f, indent=2)


def send_telegram(bot_token, chat_id, text):
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = urllib.parse.urlencode({'chat_id': chat_id, 'text': text}).encode()
    req = urllib.request.Request(url, data=payload, method='POST')
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def parse_start_utc(start_iso):
    import pytz
    start = datetime.fromisoformat(start_iso)
    if start.tzinfo is None:
        start = pytz.timezone('America/New_York').localize(start)
    return start.astimezone(timezone.utc)


ACTIVE_WEEKDAYS = {0, 1, 4}  # Monday, Tuesday, Friday only


def main():
    now_utc = datetime.now(timezone.utc)
    today_str = now_utc.strftime('%Y-%m-%d')

    import pytz
    today_weekday = datetime.now(pytz.timezone('America/New_York')).weekday()
    if today_weekday not in ACTIVE_WEEKDAYS:
        print(f'Reminders disabled today (weekday {today_weekday}). Skipping.')
        return

    try:
        bot_token = get_bot_token()
    except Exception as e:
        print(f'Bot token error: {e}', file=sys.stderr)
        return

    # Load existing cache before potentially refreshing (needed for cancellation detection)
    old_meetings, cached_at = load_cache()
    cache_stale = old_meetings is None or (now_utc - cached_at).total_seconds() > CACHE_TTL_MINUTES * 60

    meetings = old_meetings
    if cache_stale:
        try:
            new_meetings = fetch_todays_meetings()
        except Exception as e:
            print(f'Calendar fetch error: {e}', file=sys.stderr)
            if old_meetings is None:
                return
            new_meetings = None

        if new_meetings is not None:
            # Detect cancellations: upcoming meetings in old cache missing from new fetch
            if old_meetings is not None:
                new_ids = {m['id'] for m in new_meetings}
                for m in old_meetings:
                    if m['id'] not in new_ids:
                        start_utc = parse_start_utc(m['start_iso'])
                        if start_utc > now_utc:
                            text = f"⚠️ {m['name']} has been cancelled"
                            try:
                                send_telegram(bot_token, TELEGRAM_CHANNEL, text)
                                print(f"Sent cancellation: {m['name']}")
                            except Exception as e:
                                print(f"Failed to send cancellation for '{m['name']}': {e}", file=sys.stderr)

            save_cache(new_meetings)
            meetings = new_meetings

    # Load sent log, prune entries from previous days
    sent = load_sent()
    sent = {k: v for k, v in sent.items() if v == today_str}

    new_sends = False

    for meeting in meetings:
        sent_key = f"{meeting['id']}|{meeting['start_iso']}"
        if sent_key in sent:
            continue

        start_utc = parse_start_utc(meeting['start_iso'])
        minutes_until = (start_utc - now_utc).total_seconds() / 60

        # Window: 10-17 min covers any 5-minute cron slot around the 15-min mark
        if 10 <= minutes_until <= 17:
            meet_link = meeting.get('meet_link', '')
            text = f"{meeting['name']} is starting in 15'"
            if meet_link:
                text += f"\n{meet_link}"
            try:
                send_telegram(bot_token, TELEGRAM_CHANNEL, text)
                sent[sent_key] = today_str
                new_sends = True
                print(f"Sent reminder: {meeting['name']}")
            except Exception as e:
                print(f"Failed to send reminder for '{meeting['name']}': {e}", file=sys.stderr)

    if new_sends:
        save_sent(sent)


if __name__ == '__main__':
    main()
