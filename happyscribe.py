#!/usr/bin/env python3
"""Pull and process transcripts from HappyScribe API."""

import os
import requests
from datetime import datetime, date

from config import HAPPYSCRIBE_API_KEY

BASE_URL = 'https://www.happyscribe.com/api/v1'

HEADERS = {
    'Authorization': f'Bearer {HAPPYSCRIBE_API_KEY}',
    'Content-Type': 'application/json',
}


ORGANIZATION_ID = os.getenv('HAPPYSCRIBE_ORG_ID', '21612080')


def list_transcriptions(created_after=None):
    """List recent transcriptions."""
    params = {'organization_id': ORGANIZATION_ID}
    if created_after:
        params['created_after'] = created_after.isoformat()

    resp = requests.get(f'{BASE_URL}/transcriptions', headers=HEADERS, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json().get('results', [])


def get_transcription(transcription_id):
    """Get a single transcription's details."""
    resp = requests.get(f'{BASE_URL}/transcriptions/{transcription_id}', headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()


def export_transcript_text(transcription_id):
    """Export transcript as plain text."""
    resp = requests.get(
        f'{BASE_URL}/transcriptions/{transcription_id}/export',
        headers=HEADERS,
        params={'format': 'txt'},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.text


def find_todays_transcripts(meeting_date=None):
    """Find all transcripts created today (or on specified date)."""
    if meeting_date is None:
        meeting_date = date.today()

    all_transcripts = list_transcriptions(created_after=meeting_date)

    todays = []
    for t in all_transcripts:
        created = t.get('created_at', '')
        if meeting_date.isoformat() in created:
            todays.append(t)

    return todays


def match_transcript_to_project(transcript, projects):
    """Try to match a transcript to a project by name or time."""
    name = (transcript.get('name', '') or '').lower()

    for project in projects:
        project_lower = project['name'].lower()
        short_lower = project['short_name'].lower()
        if project_lower in name or short_lower in name:
            return project

    return None


if __name__ == '__main__':
    print('Checking HappyScribe connection...')
    try:
        transcripts = list_transcriptions()
        print(f'Found {len(transcripts)} transcriptions')
        for t in transcripts[:5]:
            print(f'  - {t.get("name", "unnamed")} ({t.get("state", "unknown")})')
    except Exception as e:
        print(f'Error: {e}')
