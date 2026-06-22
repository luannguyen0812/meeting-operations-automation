#!/usr/bin/env python3
"""Upload generated .docx templates to Google Drive project folders."""

import os
import json
import sys
from datetime import datetime, timedelta

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from config import PROJECTS, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

TOKEN_PATH = os.path.join(os.path.dirname(__file__), 'token.json')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')


def get_credentials():
    if not os.path.exists(TOKEN_PATH):
        print('No token.json found. Run google_auth.py first.')
        sys.exit(1)

    with open(TOKEN_PATH) as f:
        token_data = json.load(f)

    creds = Credentials(
        token=token_data['token'],
        refresh_token=token_data['refresh_token'],
        token_uri=token_data['token_uri'],
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_data['token'] = creds.token
        with open(TOKEN_PATH, 'w') as f:
            json.dump(token_data, f, indent=2)

    return creds


def find_or_create_archive_subfolder(service, parent_folder_id):
    """Find or create the 'Previous Meeting Agendas and Minutes' subfolder."""
    query = (
        f"'{parent_folder_id}' in parents "
        f"and mimeType='application/vnd.google-apps.folder' "
        f"and name='Previous Meeting Agendas and Minutes' "
        f"and trashed=false"
    )
    results = service.files().list(q=query, fields='files(id, name)').execute()
    files = results.get('files', [])
    if files:
        return files[0]['id']
    folder = service.files().create(
        body={
            'name': 'Previous Meeting Agendas and Minutes',
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_folder_id],
        },
        fields='id',
    ).execute()
    print(f'  Created archive subfolder.')
    return folder['id']


def archive_old_templates(service, parent_folder_id, archive_folder_id, date_str):
    """Move old agenda/minutes files to archive subfolder."""
    if not archive_folder_id:
        return

    query = (
        f"'{parent_folder_id}' in parents "
        f"and mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document' "
        f"and (name contains 'Meeting Agenda' or name contains 'Meeting Minutes') "
        f"and not name contains '{date_str}' "
        f"and trashed=false"
    )
    results = service.files().list(q=query, fields='files(id, name, parents)').execute()
    old_files = results.get('files', [])

    for f in old_files:
        service.files().update(
            fileId=f['id'],
            addParents=archive_folder_id,
            removeParents=parent_folder_id,
            fields='id, parents'
        ).execute()
        print(f'  Archived: {f["name"]}')


def find_existing_file(service, filename, folder_id):
    """Return the first file matching name in folder, or None."""
    query = (
        f"'{folder_id}' in parents "
        f"and name='{filename}' "
        f"and trashed=false"
    )
    results = service.files().list(q=query, fields='files(id, name, webViewLink)').execute()
    files = results.get('files', [])
    return files[0] if files else None


def upload_file(service, file_path, folder_id):
    """Upload a .docx file to Google Drive, skipping if it already exists."""
    filename = os.path.basename(file_path)

    existing = find_existing_file(service, filename, folder_id)
    if existing:
        print(f'  Skipped (already exists): {filename}')
        return existing

    file_metadata = {
        'name': filename,
        'parents': [folder_id],
    }

    media = MediaFileUpload(
        file_path,
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        resumable=True,
    )

    uploaded = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, name, webViewLink',
    ).execute()

    return uploaded


def main():
    if len(sys.argv) > 1:
        target_date = datetime.strptime(sys.argv[1], '%Y-%m-%d').date()
    else:
        target_date = datetime.now().date() + timedelta(days=1)

    date_str = target_date.strftime('%m.%d.%Y')

    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)

    print(f'Uploading templates for {target_date.strftime("%A, %B %d, %Y")}...\n')

    results = []

    for project in PROJECTS:
        project_dir = os.path.join(OUTPUT_DIR, project['short_name'])
        agenda_path = os.path.join(project_dir, f'Meeting Agenda {date_str}.docx')
        minutes_path = os.path.join(project_dir, f'Meeting Minutes {date_str}.docx')

        if not os.path.exists(agenda_path) or not os.path.exists(minutes_path):
            print(f'✗ {project["short_name"]}: files not found in {project_dir}')
            continue

        folder_id = project['drive_folder_id']

        # Archive old templates
        archive_id = find_or_create_archive_subfolder(service, folder_id)
        if archive_id:
            archive_old_templates(service, folder_id, archive_id, date_str)

        # Upload agenda
        agenda = upload_file(service, agenda_path, folder_id)
        print(f'✓ {project["short_name"]} Agenda  → {agenda["id"]}')

        # Upload minutes
        minutes = upload_file(service, minutes_path, folder_id)
        print(f'✓ {project["short_name"]} Minutes → {minutes["id"]}')

        results.append({
            'project': project['short_name'],
            'agenda_id': agenda['id'],
            'minutes_id': minutes['id'],
            'agenda_link': agenda.get('webViewLink', ''),
            'minutes_link': minutes.get('webViewLink', ''),
        })

    print(f'\nUploaded {len(results) * 2} files to Google Drive.')
    return results


if __name__ == '__main__':
    main()
