"""Driver Flask application."""
import os
import sys

from dotenv import load_dotenv
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

from .calendly_service import get_time_slots
from .google_calendar_service import create_google_calendar_event


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

# Store Twilio phone numbers
twilio_incoming_number = os.getenv('TWILIO_INCOMING_PHONE_NUMBER')
twilio_outgoing_number = os.getenv('TWILIO_PHONE_NUMBER')


"""Route definitions"""

# Test route
@app.route('/')
def index():
    return "Yay it works!"


@app.route('/sms', methods=['GET', 'POST'])
def get_availability():
    #  Send SMS with the time slots
    time_slots = str(get_time_slots())
    response = MessagingResponse()
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


if __name__ == '__main__':
    app.run(debug=True)
