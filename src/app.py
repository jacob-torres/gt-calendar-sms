"""Driver Flask application."""
from flask import Flask

# App initialization
app = Flask(__name__)


# Create app route sms with methods GET and POST
# Define a function: get_availability
# Store the sender's number in a variable
# Access Calendly calendar and store the last 3 empty time slots in a variable
# Send the time slots to the sender in an SMS message
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
