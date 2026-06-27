import os
from dotenv import load_dotenv

ENV_PATH = os.path.join(os.path.dirname(__file__), '..', '..', '.env.intrastack')
load_dotenv(ENV_PATH)

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
HAPPYSCRIBE_API_KEY = os.getenv('HAPPYSCRIBE_API_KEY')
ZAPIER_OUTLOOK_WEBHOOK = os.getenv('ZAPIER_OUTLOOK_WEBHOOK')
OUTLOOK_SENDER = os.getenv('OUTLOOK_SENDER', 'l.mnguyen@outlook.com')

PROJECTS = [
    {
        "name": "Intrastack Website Project",
        "short_name": "Intrastack Website",
        "time": "10:30–11:00 AM EDT",
        "meet_link": "https://meet.google.com/ngt-hrnf-mzu",
        "drive_folder_id": "1sxB-0wxPgBxVc8HvM9wcu7NzNO4swu56",
        "facilitator": "Luan Nguyen",
        "attendees": [
            "Arian Tashakkor", "Hayden Jose", "Duc Duy Pham", "Steve Do",
            "Aviv Shrestha", "Auspicious Munemo", "Luan Nguyen",
            "Faizan Syed", "Rishit Nagula", "Akin Korkmaz"
        ],
        "emails": [
            "arian.tashakkor@intrastack.com", "hayden.jose@intrastack.com",
            "duy.pham@intrastack.com", "steve.do@intrastack.com",
            "aviv.shrestha@intrastack.com", "auspicious.munemo@intrastack.com",
            "luan.nguyen@intrastack.com", "faizan.syed@intrastack.com",
            "rishit.nagula@intrastack.com", "akin.korkmaz@intrastack.com"
        ],
    },
    {
        "name": "AI Meeting Transcriber Platform",
        "short_name": "AI Transcriber",
        "time": "11:00–11:30 AM EDT",
        "meet_link": "https://meet.google.com/uph-bvex-kgn",
        "drive_folder_id": "1pvaeJFynY4S3cTFnZM2dvTHx_5iOHP_o",
        "facilitator": "Luan Nguyen",
        "attendees": [
            "Nicolas Cadena", "Auspicious Munemo", "Luan Nguyen",
            "Danny Ngo", "Samir Kazma", "Simon Truong"
        ],
        "emails": [
            "nicolas.cadena@intrastack.com", "auspicious.munemo@intrastack.com",
            "luan.nguyen@intrastack.com", "danny.ngo@intrastack.com",
            "samir.kazma@intrastack.com", "simon.truong@intrastack.com"
        ],
    },
    {
        "name": "Tekstack Academy Project",
        "short_name": "Tekstack Academy",
        "time": "11:30 AM–12:00 PM EDT",
        "meet_link": "https://meet.google.com/geq-qudf-jyn",
        "drive_folder_id": "1nUNBYSqEkvYtGHJcg7C1oTqpBFNkwzZ4",
        "facilitator": "Luan Nguyen",
        "attendees": [
            "Caleb Berent", "Givens Raymond", "Jack Dai", "Josh Lowe",
            "Nicolas Cadena", "Victoria Pham", "Vashrith Vinodh",
            "Emilio Arellano", "Xinren Ai", "Duc Duy Pham", "Steve Do",
            "Auspicious Munemo", "Luan Nguyen", "Danny Ngo", "Samir Kazma"
        ],
        "emails": [
            "caleb.berent@intrastack.com", "givens.raymond@intrastack.com",
            "jack.dai@intrastack.com", "josh.lowe@intrastack.com",
            "nicolas.cadena@intrastack.com", "victoria.pham@intrastack.com",
            "vashrith.vinodh@intrastack.com", "emilio.arellano@intrastack.com",
            "xinren.ai@intrastack.com", "duy.pham@intrastack.com",
            "steve.do@intrastack.com", "auspicious.munemo@intrastack.com",
            "luan.nguyen@intrastack.com", "danny.ngo@intrastack.com",
            "samir.kazma@intrastack.com"
        ],
    },
    {
        "name": "Dragon Point of Sale System",
        "short_name": "Dragon POS",
        "time": "12:00–12:30 PM EDT",
        "meet_link": "https://meet.google.com/pry-hjbp-xmi",
        "drive_folder_id": "1k5LtdobK847uVkpcXgbQFw-aedrBsdda",
        "facilitator": "Luan Nguyen",
        "attendees": [
            "Ali Hussain", "Arian Tashakkor", "Arjun Sherugar", "Christian Artigas",
            "Hayden Jose", "Jack Dai", "Zainab Syed", "Josh Lowe",
            "Victoria Pham", "Vashrith Vinodh", "Steve Do", "Aviv Shrestha",
            "Sydney Hall", "Auspicious Munemo", "Luan Nguyen",
            "Faizan Syed", "Gaurav Nath", "Rishit Nagula", "Simon Truong"
        ],
        "emails": [
            "ali.hussain@intrastack.com", "arian.tashakkor@intrastack.com",
            "arjun.sherugar@intrastack.com", "christian.artigas@intrastack.com",
            "hayden.jose@intrastack.com", "jack.dai@intrastack.com",
            "zainab.syed@intrastack.com", "josh.lowe@intrastack.com",
            "victoria.pham@intrastack.com", "vashrith.vinodh@intrastack.com",
            "steve.do@intrastack.com", "aviv.shrestha@intrastack.com",
            "sydney.hall@intrastack.com", "auspicious.munemo@intrastack.com",
            "luan.nguyen@intrastack.com", "faizan.syed@intrastack.com",
            "gaurav.nath@intrastack.com", "rishit.nagula@intrastack.com",
            "simon.truong@intrastack.com"
        ],
    },
    {
        "name": "Agentic AI Global News Platform",
        "short_name": "Agentic AI",
        "time": "2:30–3:00 PM EDT",
        "meet_link": "https://meet.google.com/iex-sbjg-zoz",
        "drive_folder_id": "12iMWRHgniQuKz7DHo972dT6hW3VlAIDq",
        "facilitator": "Luan Nguyen",
        "attendees": [
            "Nicolas Cadena", "Marvin Nguyen", "Victoria Pham",
            "Aviv Shrestha", "Auspicious Munemo", "Luan Nguyen",
            "Thao Nguyen", "Rishit Nagula"
        ],
        "emails": [
            "nicolas.cadena@intrastack.com", "marvin.nguyen@intrastack.com",
            "victoria.pham@intrastack.com", "aviv.shrestha@intrastack.com",
            "auspicious.munemo@intrastack.com", "luan.nguyen@intrastack.com",
            "thao.nguyen@intrastack.com", "rishit.nagula@intrastack.com"
        ],
    },
    {
        "name": "Multi Cloud Security Assessment",
        "short_name": "Multi Cloud Security",
        "time": "11:30 AM–12:00 PM EDT",
        "meet_link": "https://meet.google.com/zri-excz-zoo",
        "drive_folder_id": "1HSTOEnQxTl3KHAenXhGrblMkBaHkewzZ",
        "facilitator": "Luan Nguyen",
        "attendees": [
            "Marvin Nguyen", "Victoria Pham", "Vashrith Vinodh",
            "Jaden Jayasinghe", "Duc Duy Pham", "Steve Do", "Aviv Shrestha",
            "Auspicious Munemo", "Luan Nguyen", "Danny Ngo",
            "Samir Kazma", "Simon Truong"
        ],
        "emails": [
            "marvin.nguyen@intrastack.com", "victoria.pham@intrastack.com",
            "vashrith.vinodh@intrastack.com", "jaden.jayasinghe@intrastack.com",
            "duy.pham@intrastack.com", "steve.do@intrastack.com",
            "aviv.shrestha@intrastack.com", "auspicious.munemo@intrastack.com",
            "luan.nguyen@intrastack.com", "danny.ngo@intrastack.com",
            "samir.kazma@intrastack.com", "simon.truong@intrastack.com"
        ],
    },
    {
        "name": "Openclaw & Security",
        "short_name": "Openclaw & Security",
        "time": "6:00–6:30 PM EDT",
        "meet_link": "https://meet.google.com/fcx-yjuv-ory",
        "drive_folder_id": "1IEm4O9RxUYlRIWcGRIEWl6_XIeHLU5C2",
        "facilitator": "Auspicious Munemo",
        "attendees": [
            "Victoria Pham", "Gervyn Bengil", "Vashrith Vinodh",
            "Abdallah Daoud", "Emilio Arellano", "Jaden Jayasinghe",
            "Xinren Ai", "Ashley Uscanga", "Sydney Hall",
            "Auspicious Munemo", "Luan Nguyen", "Danny Ngo"
        ],
        "emails": [
            "victoria.pham@intrastack.com", "gervyn.bengil@intrastack.com",
            "vashrith.vinodh@intrastack.com", "abdallah.daoud@intrastack.com",
            "emilio.arellano@intrastack.com", "jaden.jayasinghe@intrastack.com",
            "xinren.ai@intrastack.com", "ashley.uscanga@intrastack.com",
            "sydney.hall@intrastack.com", "auspicious.munemo@intrastack.com",
            "luan.nguyen@intrastack.com", "danny.ngo@intrastack.com"
        ],
    },
    {
        "name": "BidOps AI",
        "short_name": "BidOps AI",
        "time": "T 9:00–9:30 PM / TH 7:00–7:30 PM EDT",
        "meet_link": "https://meet.google.com/muy-zxoa-vqp",
        "drive_folder_id": "1PdaY2IaUfYyne-y4RmpRwQREfb48LiEP",
        "facilitator": "Luan Nguyen",
        "attendees": [
            "Chandler Beaubrun", "Christian Artigas", "Josh Lowe",
            "Nicolas Cadena", "Marvin Nguyen", "Duc Duy Pham",
            "Auspicious Munemo", "Luan Nguyen"
        ],
        "emails": [
            "chandler.beaubrun@intrastack.com", "christian.artigas@intrastack.com",
            "josh.lowe@intrastack.com", "nicolas.cadena@intrastack.com",
            "marvin.nguyen@intrastack.com", "duy.pham@intrastack.com",
            "auspicious.munemo@intrastack.com", "luan.nguyen@intrastack.com"
        ],
    },
    {
        "name": "DevOps/Cloud Automation",
        "short_name": "DevOps Cloud",
        "time": "W 4:00–4:30 PM / S 5:30–6:00 PM EDT",
        "meet_link": "https://meet.google.com/pfb-hekf-oja",
        "drive_folder_id": "1RvOBYEaDp0mRV4zHHKm62nUQHWRHCANM",
        "facilitator": "Luan Nguyen",
        "attendees": [
            "Likitha Reddy", "Christian Rodriguez", "Victoria Pham",
            "Marvin Nguyen"
        ],
        "emails": [
            "liktha.mettu@intrastack.com", "christian.rodriguez@intrastack.com",
            "victoria.pham@intrastack.com", "marvin.nguyen@intrastack.com",
            "luan.nguyen@intrastack.com"
        ],
    },
    {
        "name": "Customize Odoo CRM",
        "short_name": "Odoo CRM",
        "time": "",
        "meet_link": "",
        "drive_folder_id": "1iqI-N9U4JCb_dXR_8zi_Y2XVKhhKAqKu",
        "facilitator": "Luan Nguyen",
        "attendees": [
            "Arian Tashakkor", "Steve Do", "Auspicious Munemo",
            "Luan Nguyen", "Rishit Nagula"
        ],
        "emails": [
            "arian.tashakkor@intrastack.com", "steve.do@intrastack.com",
            "auspicious.munemo@intrastack.com", "luan.nguyen@intrastack.com",
            "rishit.nagula@intrastack.com"
        ],
    },
    {
        "name": "AI Staffing & Automation Platform",
        "short_name": "AI Staffing",
        "time": "",
        "meet_link": "",
        "drive_folder_id": "1VjjnicccOuJR0ltp4riNKY20ZpgkxptC",
        "facilitator": "Luan Nguyen",
        "attendees": [],
        "emails": ["luan.nguyen@intrastack.com"],
    },
    {
        "name": "IntracodeX Platform",
        "short_name": "IntracodeX",
        "time": "",
        "meet_link": "",
        "drive_folder_id": "1kg9RWyhUBkTQI_9oe-0gL790YaS6WOUb",
        "facilitator": "Luan Nguyen",
        "attendees": [
            "Jack Dai", "Marvin Nguyen", "Victoria Pham", "Alaan Kallab",
            "Christian Scott", "Aviv Shrestha", "Auspicious Munemo",
            "Luan Nguyen", "Thao Nguyen", "Danny Ngo", "Faizan Syed",
            "Rishit Nagula", "Simon Truong", "Sudeep Thatiparthi", "Raymond Ha"
        ],
        "emails": [
            "jack.dai@intrastack.com", "marvin.nguyen@intrastack.com",
            "victoria.pham@intrastack.com", "alaan.kallab@intrastack.com",
            "christian.scott@intrastack.com", "aviv.shrestha@intrastack.com",
            "auspicious.munemo@intrastack.com", "luan.nguyen@intrastack.com",
            "thao.nguyen@intrastack.com", "danny.ngo@intrastack.com",
            "faizan.syed@intrastack.com", "rishit.nagula@intrastack.com",
            "simon.truong@intrastack.com", "sudeep.thatiparthi@intrastack.com",
            "raymond.ha@intrastack.com"
        ],
    },
    {
        "name": "Moodle LMS Project",
        "short_name": "Moodle LMS",
        "time": "",
        "meet_link": "",
        "drive_folder_id": "1dEf0wMGItksZ3qpnehGbJYWm6r-oTLzo",
        "facilitator": "Luan Nguyen",
        "attendees": [
            "Arian Tashakkor", "Alaan Kallab", "Auspicious Munemo",
            "Luan Nguyen", "Faizan Syed", "Rishit Nagula"
        ],
        "emails": [
            "arian.tashakkor@intrastack.com", "alaan.kallab@intrastack.com",
            "auspicious.munemo@intrastack.com", "luan.nguyen@intrastack.com",
            "faizan.syed@intrastack.com", "rishit.nagula@intrastack.com"
        ],
    },
]

def _apply_roster_cache():
    """Overlay cached spreadsheet emails/attendees onto PROJECTS."""
    cache_path = os.path.join(os.path.dirname(__file__), 'roster_cache.json')
    if not os.path.exists(cache_path):
        return
    try:
        import json as _json
        with open(cache_path) as f:
            cached = _json.load(f).get('projects', {})
        for project in PROJECTS:
            entry = cached.get(project['name'])
            if entry and entry.get('emails'):
                project['emails'] = entry['emails']
            if entry and entry.get('attendees'):
                project['attendees'] = entry['attendees']
    except Exception:
        pass

_apply_roster_cache()

AGENDA_ROWS = [
    ("1", "Review of current tasks and priorities", "Scrum Master", "5 min"),
    ("2", "Progress updates since the last meeting", "Project Lead / Team Members", "5 min"),
    ("3", "Issues and challenges encountered", "Scrum Master / Project Lead", "5 min"),
    ("4", "Roadblocks requiring support or escalation", "Scrum Master / Project Lead", "5 min"),
    ("5", "Upcoming milestones and deliverables", "Project Lead", "5 min"),
    ("6", "Announcements and key updates", "Scrum Master", "5 min"),
]
