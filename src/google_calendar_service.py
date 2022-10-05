"""Module for accessing the Google Calendar API."""
import os
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Error with accessing credentials and token JSON files
    # SCOPES = ['https://www.googleapis.com/auth/calendar.events']
# creds = None
# if os.path.exists('token.json'):
    # creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
# if not creds or not creds.valid:
    # if creds and creds.expired and creds.refresh_token:
        # creds.refresh(Request())
    # else:
        # flow = InstalledAppFlow.from_client_secrets_file(
            # 'credentials.json', SCOPES)
        # creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    # with open('token.json', 'w') as token:
        # token.write(creds.to_json())

try:
    SCOPES = ['https://www.googleapis.com/auth/calendar.events']
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    google_calendar_service = build('calendar', 'v3', credentials=creds)
except HttpError as error:
    print(error)


# Create a new event in the Google calendar in the selected time slot
def create_google_calendar_event(time_slot: dict) -> bool:
    """Matches the events in the Google calendar with the selected time slot
    and, if available, creates a new event for that time.

    parameters
    ----------
    time_slot : dict
    The selected time slot as a dictionary of datetime strings

    returns
    -------
    bool : True if successful, False if not
    """
    # Convert time slot start and end into datetime objects
    slot_start = datetime.strptime(time_slot['from'], dt_format)
    slot_end = datetime.strptime(time_slot['to'], dt_format)

    # The event to be added to the Google calendar
    new_event = {
        'description': 'Hang Out',
        'start': {
            'dateTime': time_slot['from']
        },
        'end': {
            'dateTime': time_slot['to']
        }
    }

    # Get existing Google calendar events
    events_result = google_calendar_service.events().list(calendarId='primary')
    events = events_result.get('items', [])

    if not events:
        google_calendar_service.events().insert(
            calendarId='primary',
            body=new_event
        ).execute()
        return True

    else:
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))

            dt_format = '%Y-%m-%dT%H:%M:%S'
            event_start = datetime.strptime(start, dt_format)
            event_end = datetime.strptime(end, dt_format)

            # Check that the selected time slot doesn't conflict with the event
            if slot_start.hour > event_end.hour or slot_end.hour < event_start.hour:
                google_calendar_service.events().insert(
                    calendarId='primary',
                    body=new_event
                ).execute()
                return True

    return False


# TODO:
# The app sends the sender a success message with the selected time slot
# If the corresponding time slot is not available, the app sends another SMS to the sender asking them to choose a different number
# The same process is repeated until a time slot is available, or until all time slots are unavailable
# If no time slots are available, the application closes with a final failure message
