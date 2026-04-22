from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


def authenticate_google_calendar():
    SCOPES = ['https://www.googleapis.com/auth/calendar']

    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES)

    creds = flow.run_local_server(port=0)

    with open('token.json', 'w') as token:
        token.write(creds.to_json())

def create_event(summary, start_time, end_time):
    creds = Credentials.from_authorized_user_file('tools/reminder/token.json')
    service = build('calendar', 'v3', credentials=creds)

    event = {
        'summary': summary,
        'start': {
            'dateTime': start_time,
            'timeZone': 'Asia/Kolkata'
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Asia/Kolkata'
        },
    }

    created_event = service.events().insert(
        calendarId='primary',
        body=event
    ).execute()

    # print("CREATED EVENT:", created_event)

    return created_event