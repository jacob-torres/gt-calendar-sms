"""Module for accessing the Calendly API."""
import os
from datetime import datetime, timedelta

from calendly import Calendly
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

calendly_access_token = os.getenv('CALENDLY_ACCESS_TOKEN')
calendly_user_uri = os.getenv('CALENDLY_USER_URI')
calendly = Calendly(calendly_access_token)


# Access Calendly calendar and return the last 3 empty time slots
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
        # and subtract 4 hours for Eastern timezone
        start_time = datetime.strptime(
            event['start_time'][:dt_endpoint], dt_format
        ) - timedelta(hours=4)
        end_time = datetime.strptime(
            event['end_time'][:dt_endpoint], dt_format
        ) - timedelta(hours=4)

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
