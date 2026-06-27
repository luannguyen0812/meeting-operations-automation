#!/usr/bin/env python3
"""One-time Google OAuth setup. Run this once to generate token.json."""

import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

TOKEN_PATH = os.path.join(os.path.dirname(__file__), 'token.json')
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/calendar.readonly',
]


def get_client_config():
    return {
        "installed": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"]
        }
    }


def authenticate():
    flow = InstalledAppFlow.from_client_config(get_client_config(), SCOPES)
    creds = flow.run_local_server(port=8090, prompt='consent')

    token_data = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes,
    }
    with open(TOKEN_PATH, 'w') as f:
        json.dump(token_data, f, indent=2)

    print(f'Authentication successful. Token saved to {TOKEN_PATH}')
    return creds


if __name__ == '__main__':
    authenticate()
