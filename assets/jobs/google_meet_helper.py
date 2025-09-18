import uuid
from google.oauth2 import service_account
from googleapiclient.discovery import build

def create_google_meet_event(title, description, start_time, end_time):
    """
    Creates a Google Calendar event with a Meet link using a service account.
    Requires service account to have access to a calendar.
    """
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    SERVICE_ACCOUNT_FILE = 'config/credentials/qubits-hrms-project-55ac80f67d7d.json'  # Change this path if needed

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )

    # Use the calendar of the service account itself (not the user)
    delegated_credentials = credentials.with_subject('<service_account_email>')  # Optional if needed
    service = build('calendar', 'v3', credentials=credentials)

    # Create the event with Google Meet link
    event = {
        'summary': title,
        'description': description,
        'start': {
            'dateTime': start_time,
            'timeZone': 'Asia/Kolkata',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Asia/Kolkata',
        },
        'conferenceData': {
            'createRequest': {
                'conferenceSolutionKey': {
                    'type': 'hangoutsMeet'
                },
                'requestId': f"meet-{uuid.uuid4().hex[:10]}"
            }
        }
    }

    created_event = service.events().insert(
        calendarId='primary',
        body=event,
        conferenceDataVersion=1
    ).execute()

    return created_event.get('hangoutLink')
