"""Driver Flask application."""
import os
import sys
from datetime import datetime, timedelta

from calendly import Calendly
from dotenv import load_dotenv
from flask import Flask, request
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse


# Load environment variables
load_dotenv()

# Initialize and configure app
app = Flask(__name__)
app.config.from_mapping(
    BASE_URL="http://localhost:5000",
    ENV="development",
    USE_NGROK=os.getenv('USE_NGROK', False) == "True"
)

# Import and initialize pyngrok for HTTP tunneling
# only if in development environment and if USE_NGROK is True
if app.config.get('ENV') == "development" and app.config['USE_NGROK']:
    from pyngrok import ngrok

    # Assign port number from command line arg or default
    port = sys.argv(
        sys.argv.index('--port') + 1
    ) if '--port' in sys.argv else 5000

    # Get ngrok public URL
    public_url = ngrok.connect(port).public_url

    print(f" * ngrok HTTP tunnel started at {public_url}"
                            f" from http://127.0.0.1:{port}")

    # Change base URL to the new ngrok URL
    app.config['BASE_URL'] = public_url

# Connect to Twilio API
# Possibly removing because the Twilio client may not be used
twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_incoming_number = "+17205821400"
twilio_outgoing_number = os.getenv('TWILIO_PHONE_NUMBER')
twilio_client = Client(twilio_account_sid, twilio_auth_token)

# Connect to Calendly API
calendly_access_token = os.getenv('CALENDLY_ACCESS_TOKEN')
calendly_user_uri = os.getenv('CALENDLY_USER_URI')
calendly = Calendly(calendly_access_token)

# Connect to Google Calendar API
scopes = ['https://www.googleapis.com/auth/calendar.events']
# Look for token file, or create if it does not exist
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', scopes)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scopes)
        creds = flow.run_local_server(port=0)

    # Save credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

try:
    google_calendar_service = build('calendar', 'v3', credentials=creds)
except HttpError as error:
    print(error)

"""Route definitions"""

# Test route
@app.route('/')
def index():
    return "Yay it works!"


@app.route('/sms', methods=['GET', 'POST'])
def get_availability():
    response = MessagingResponse()

    # Get the last 3 available time slots
    time_slots = str(get_time_slots())

    # Send the time slots to the sender in an SMS message
    response_body = f"""
    Your buddy is available during the following times:

    {time_slots}
    """

    response.message(
        to=twilio_incoming_number,
        from_=twilio_outgoing_number,
        body=response_body
    )

    return str(response)


# Access Calendly calendar and store the last 3 empty time slots
def get_time_slots():
    # Events are hard-coded below which contain only relevant properties
    # When there are events in Calendly, the code will work the same
    # events = calendly.list_events(calendly_user_uri)
    events = [
        {
                'end_time': '2022-10-05T15:00:00.000000Z',
                'start_time': '2022-10-05T14:00:00.000000Z',
        },

        {
                'end_time': '2022-10-05T18:00:00.000000Z',
                'start_time': '2022-10-05T17:00:00.000000Z',
        },

        {
                'end_time': '2022-10-05T22:00:00.000000Z',
                'start_time': '2022-10-05T21:00:00.000000Z',
        },

        {
                'end_time': '2022-10-06T02:00:00.000000Z',
                'start_time': '2022-10-06T01:00:00.000000Z',
        },

        {
                'end_time': '2022-10-06T15:00:00.000000Z',
                'start_time': '2022-10-06T14:00:00.000000Z',
        },

        {
                'end_time': '2022-10-06T20:00:00.000000Z',
                'start_time': '2022-10-06T18:00:00.000000Z',
        },

        {
                'end_time': '2022-10-07T00:00:00.000000Z',
                'start_time': '2022-10-06T23:00:00.000000Z',
        }
    ]

    # Define empty time slots
    prev_time = datetime.today()
    time_slots = []
    dt_format = '%Y-%m-%dT%H:%M:%S'
    # The parsable datetime ends at the index of the first '.' character
    dt_endpoint = events[0]['end_time'].find('.')

    for event in events:
        # Format each event start and end times as datetime objects
        # and subtract 6 hours for mountain timezone
        start_time = datetime.strptime(
            event['start_time'][:dt_endpoint], dt_format
        ) - timedelta(hours=6)
        end_time = datetime.strptime(
            event['end_time'][:dt_endpoint], dt_format
        ) - timedelta(hours=6)

        if (start_time - prev_time).seconds / 3600 >= 3.0:
            new_time = start_time - timedelta(hours=3)
            slot = {
                'from': new_time.strftime(dt_format),
                'to': start_time.strftime(dt_format)
            }
            time_slots.append(slot)

            # Only include time slots between 8:00 and 22:00
            slot_start = datetime.strptime(slot['from'], dt_format)
            if slot_start.hour < 8 or slot_start.hour > 22:
                time_slots.remove(slot)

        prev_time = end_time

    # Get last 3 time slots
    time_slots = time_slots[-3:]
    return time_slots


# Create a new event in the Google calendar in the selected time slot
def create_google_calendar_event(time_slot):
    # Convert time slot start and end into datetime objects
    slot_start = datetime.strptime(time_slot['from'], dt_format)
    slot_end = datetime.strptime(time_slot['to'], dt_format)
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
# Message the sender to reply with 1, 2, or 3 to select a time slot
#  The sender's selection is stored in a variable once received
# The Google calendar is accessed and the time slot is checked for availability
# If the corresponding Google calendar entry is available, the selected time slot is used to save a new event in the Google calendar
# The app sends the sender a success message with the selected time slot
# If the corresponding time slot is not available, the app sends another SMS to the sender asking them to choose a different number
# The same process is repeated until a time slot is available, or until all time slots are unavailable
# If no time slots are available, the application closes with a final failure message


if __name__ == '__main__':
    app.run(debug=True)
