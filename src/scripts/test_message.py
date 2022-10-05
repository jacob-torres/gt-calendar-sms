import os

from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
phone_number = os.environ['TWILIO_PHONE_NUMBER']
client = Client(account_sid, auth_token)

message = client.messages.create(
    to="+17205821400",
    from_=phone_number,
    body="Hello from Python!"
)

print(message.sid)