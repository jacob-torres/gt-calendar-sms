"""Driver Flask application."""
import os
import sys

from dotenv import load_dotenv
from flask import Flask, request
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
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
outgoing_phone = os.getenv('TWILIO_PHONE_NUMBER')
client = Client(account_sid, auth_token)

"""Route definitions"""

# Test route
@app.route('/')
def index():
    return "Yay it works!"


@app.route('/sms', methods=['GET', 'POST'])
def get_availability():
    if request.method == 'POST':
        response = MessagingResponse()
        response.message(
            to="+17205821400",
            from_=outgoing_phone,
            body="This is a test of the emergency alert system."
        )

    return str(response)


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
