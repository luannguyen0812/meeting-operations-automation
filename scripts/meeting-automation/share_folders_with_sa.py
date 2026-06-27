#!/usr/bin/env python3
"""
One-time script: share all project Drive folders with the service account.
Run once with valid user OAuth token, then never needed again.
"""

import json
import os
import sys
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

sys.path.insert(0, os.path.dirname(__file__))
from config import PROJECTS, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from sa_auth import _INTERN_BOT_SA

TOKEN_PATH = os.path.join(os.path.dirname(__file__), 'token.json')
PARENT_FOLDER_ID = '1M1uhRL-esinT0ziySAaQmyaUzCeJicRl'
PM_PRIVATE_FOLDER_ID = '1ZTwtu6xLH_Hp-6kOhLVmF76X8QF6t2Au'

with open(_INTERN_BOT_SA) as f:
    SA_EMAIL = json.load(f)['client_email']


def get_credentials():
    with open(TOKEN_PATH) as f:
        td = json.load(f)
    creds = Credentials(
        token=td['token'], refresh_token=td['refresh_token'],
        token_uri=td['token_uri'], client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        td['token'] = creds.token
        with open(TOKEN_PATH, 'w') as f:
            json.dump(td, f, indent=2)
    return creds


def share_folder(service, folder_id, folder_name):
    try:
        service.permissions().create(
            fileId=folder_id,
            body={'type': 'user', 'role': 'writer', 'emailAddress': SA_EMAIL},
            fields='id',
            sendNotificationEmail=False,
        ).execute()
        print(f'  ✓ {folder_name}')
    except Exception as e:
        print(f'  ✗ {folder_name}: {e}')


def main():
    print(f'Sharing folders with: {SA_EMAIL}\n')
    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)

    # Share parent folder (covers any top-level structure)
    share_folder(service, PARENT_FOLDER_ID, 'Parent folder')

    # Share private PM folder (Project Team spreadsheet lives here)
    share_folder(service, PM_PRIVATE_FOLDER_ID, 'PM Private folder (Project Team spreadsheet)')

    # Share each project folder individually
    seen = set()
    for project in PROJECTS:
        fid = project.get('drive_folder_id')
        if fid and fid not in seen:
            share_folder(service, fid, project['short_name'])
            seen.add(fid)

    print(f'\nDone. The service account now has write access to all {len(seen) + 1} folders.')
    print('You can delete this script and token.json after this.')


if __name__ == '__main__':
    main()
