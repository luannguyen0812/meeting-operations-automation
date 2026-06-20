import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
HAPPYSCRIBE_API_KEY = os.getenv('HAPPYSCRIBE_API_KEY')
ZAPIER_OUTLOOK_WEBHOOK = os.getenv('ZAPIER_OUTLOOK_WEBHOOK')
OUTLOOK_SENDER = os.getenv('OUTLOOK_SENDER', 'your.email@outlook.com')

# Add your own projects below. Each entry drives the full pipeline:
# reminders, agenda docs, transcript matching, meeting minutes, and Drive upload.
# - name: must match the corresponding tab name in your team roster Google Sheet
# - drive_folder_id: copy from the URL of your target Drive folder
PROJECTS = [
    {
        "name": "Example Project Alpha",
        "short_name": "Project Alpha",
        "time": "10:00–10:30 AM EDT",
        "meet_link": "https://meet.google.com/xxx-xxxx-xxx",
        "drive_folder_id": "YOUR_DRIVE_FOLDER_ID_HERE",
        "facilitator": "Jane Smith",
        "attendees": [
            "Jane Smith", "John Doe", "Alice Johnson", "Bob Chen"
        ],
        "emails": [
            "jane.smith@yourcompany.com",
            "john.doe@yourcompany.com",
            "alice.johnson@yourcompany.com",
            "bob.chen@yourcompany.com",
        ],
    },
    {
        "name": "Example Project Beta",
        "short_name": "Project Beta",
        "time": "11:00–11:30 AM EDT",
        "meet_link": "https://meet.google.com/yyy-yyyy-yyy",
        "drive_folder_id": "YOUR_DRIVE_FOLDER_ID_HERE",
        "facilitator": "John Doe",
        "attendees": [
            "John Doe", "Maria Garcia", "Sam Lee"
        ],
        "emails": [
            "john.doe@yourcompany.com",
            "maria.garcia@yourcompany.com",
            "sam.lee@yourcompany.com",
        ],
    },
]

AGENDA_ROWS = [
    ("1", "Review of current tasks and priorities", "Scrum Master", "5 min"),
    ("2", "Progress updates since the last meeting", "Project Lead / Team Members", "5 min"),
    ("3", "Issues and challenges encountered", "Scrum Master / Project Lead", "5 min"),
    ("4", "Roadblocks requiring support or escalation", "Scrum Master / Project Lead", "5 min"),
    ("5", "Upcoming milestones and deliverables", "Project Lead", "5 min"),
    ("6", "Announcements and key updates", "Scrum Master", "5 min"),
]
