"""Module for handling a time slot choice via SMS."""
from flask import Request, session
from twilio.twiml.messaging_response import Body, Message, MessagingResponse

from .app import app
from .calendly_service import get_time_slots


# For persisting SMS conversation to choose a time slot
@app.route('/directory/search', methods=['POST'])
def search():
    # Get any previous choices from the conversation
    choices = session.get('choices', [])
    query = Request.form['Body']

    if choices:
        # Call the calendly service to get a list of time slots
        time_slots = get_time_slots()
        num_slots = len(time_slots)

        if not time_slots:
            send_no_slots_message()

        if not is_valid_choice(query, num_slots):
            send_invalid_choice_message(num_slots)

        # Send the selected time slot info
        time_slot = time_slots[query - 1]
        send_success_message(time_slot)


def is_valid_choice(query, num_slots):
    if query.isdigit():
        query = int(query)
        return (query - 1) in range(num_slots)

    return False


def send_no_slots_message():
    response = MessagingResponse()
    response.message("Sorry, no open time slots available.")
    return str(response)


def send_invalid_choice_message(num_slots):
    response = MessagingResponse()
    response.message(f"Please specify a number less than {num_slots}.")
    return str(response)
    

def send_success_message(time_slot):
    response = MessagingResponse()
    response.message(
        f"Your event is scheduled for {time_slot['from']}"
        f" to {time_slot['to']}."
    )
    return str(response)
