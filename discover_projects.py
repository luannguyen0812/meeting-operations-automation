#!/usr/bin/env python3
"""
Dynamically discover projects from Google Drive folder structure + Google Sheet roster.
New projects are auto-detected when they appear in Drive with the standard folder structure.
"""

import json
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, PROJECTS as STATIC_PROJECTS

TOKEN_PATH = os.path.join(os.path.dirname(__file__), 'token.json')
PARENT_FOLDER_ID = '1M1uhRL-esinT0ziySAaQmyaUzCeJicRl'
CACHE_PATH = os.path.join(os.path.dirname(__file__), 'projects_cache.json')


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


def scan_drive_projects():
    """Scan the parent Drive folder for project folders with Meeting Agenda & Minutes subfolders."""
    creds = get_credentials()
    drive = build('drive', 'v3', credentials=creds)

    results = drive.files().list(
        q=f"'{PARENT_FOLDER_ID}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false",
        fields='files(id, name)',
        orderBy='name',
    ).execute()

    project_folders = results.get('files', [])
    discovered = []

    for folder in project_folders:
        sub_results = drive.files().list(
            q=f"'{folder['id']}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false",
            fields='files(id, name)',
        ).execute()

        subfolders = sub_results.get('files', [])
        meeting_folder = None
        archive_folder = None

        for sf in subfolders:
            name_lower = sf['name'].lower()
            if 'meeting' in name_lower and ('agenda' in name_lower or 'minutes' in name_lower):
                meeting_folder = sf
            if 'previous' in name_lower:
                archive_folder = sf

        if meeting_folder:
            discovered.append({
                'drive_project_name': folder['name'],
                'drive_project_folder_id': folder['id'],
                'drive_meeting_folder_id': meeting_folder['id'],
                'drive_archive_folder_id': archive_folder['id'] if archive_folder else None,
            })

    return discovered


def merge_with_static(discovered):
    """Merge discovered Drive projects with static config. Static wins for known projects."""
    known_folder_ids = {p['drive_folder_id'] for p in STATIC_PROJECTS}
    merged = list(STATIC_PROJECTS)

    for disc in discovered:
        if disc['drive_meeting_folder_id'] in known_folder_ids:
            continue

        merged.append({
            'name': disc['drive_project_name'],
            'short_name': disc['drive_project_name'],
            'time': '',
            'meet_link': '',
            'drive_folder_id': disc['drive_meeting_folder_id'],
            'facilitator': 'Luan Nguyen',
            'attendees': [],
            'emails': [],
            '_discovered': True,
            '_project_folder_id': disc['drive_project_folder_id'],
        })

    return merged


def get_all_projects(use_cache=True):
    """Get all projects, discovering new ones from Drive."""
    if use_cache and os.path.exists(CACHE_PATH):
        age = os.time() - os.path.getmtime(CACHE_PATH)
        if age < 86400:
            with open(CACHE_PATH) as f:
                return json.load(f)

    discovered = scan_drive_projects()
    all_projects = merge_with_static(discovered)

    with open(CACHE_PATH, 'w') as f:
        json.dump(all_projects, f, indent=2, default=str)

    return all_projects


def discover_new():
    """Find projects in Drive that aren't in the static config."""
    discovered = scan_drive_projects()
    known_folder_ids = {p['drive_folder_id'] for p in STATIC_PROJECTS}

    new_projects = []
    for disc in discovered:
        if disc['drive_meeting_folder_id'] not in known_folder_ids:
            new_projects.append(disc)

    return new_projects


if __name__ == '__main__':
    print('Scanning Google Drive for projects...\n')
    discovered = scan_drive_projects()
    known_ids = {p['drive_folder_id'] for p in STATIC_PROJECTS}

    print(f'Found {len(discovered)} projects with Meeting Agenda & Minutes folders:\n')
    for d in discovered:
        status = '✓ KNOWN' if d['drive_meeting_folder_id'] in known_ids else '★ NEW'
        print(f'  [{status}] {d["drive_project_name"]}')
        print(f'         Meeting folder: {d["drive_meeting_folder_id"]}')

    new_ones = [d for d in discovered if d['drive_meeting_folder_id'] not in known_ids]
    if new_ones:
        print(f'\n{len(new_ones)} new project(s) detected that could be added to automation.')
    else:
        print('\nNo new projects found. All Drive projects are already configured.')
