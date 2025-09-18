import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from django.conf import settings

def get_calendar_service():
    credentials = service_account.Credentials.from_service_account_file(
        str(settings.GOOGLE_SERVICE_ACCOUNT_FILE),
        scopes=settings.GOOGLE_CALENDAR_SCOPES,
    )
    return build('calendar', 'v3', credentials=credentials)

def create_meet_event(summary, description, start_datetime, end_datetime):
    service = get_calendar_service()

    event = {
        "summary": summary,
        "description": description,
        "start": {
            "dateTime": start_datetime.isoformat(),
            "timeZone": "Asia/Kolkata"
        },
        "end": {
            "dateTime": end_datetime.isoformat(),
            "timeZone": "Asia/Kolkata"
        },
        "conferenceData": {
            "createRequest": {
                "requestId": f"meet-{int(datetime.datetime.now().timestamp())}"
            }
        }
    }

    created_event = service.events().insert(
        calendarId='primary',
        body=event,
        conferenceDataVersion=1
    ).execute()

    # ✅ Safely extract the Meet link
    conference_data = created_event.get("conferenceData", {})
    entry_points = conference_data.get("entryPoints", [])

    if not entry_points:
        raise Exception("Google Meet link could not be generated. Possibly due to missing permissions or account limitations.")

    for entry in entry_points:
        if entry.get("entryPointType") == "video":
            return entry.get("uri")

    raise Exception("Google Meet link not found in entryPoints.")
