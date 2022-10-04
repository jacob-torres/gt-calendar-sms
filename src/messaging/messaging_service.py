"""Messaging service module for interacting with the rest API."""
import os

from dotenv import load_dotenv
from twilio.base.exceptions import TwilioException, TwilioRestException
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

# Load environment variables
load_dotenv()


class MessagingService:
    """Uses the Twilio rest API to perform SMS messaging."""

    def __init__(self) -> None:
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.service_phone_number = os.getenv('TWILIO_PHONE_NUMBER')
        self.sender_phone_number = ''

        # Check that the credentials/environment variables exist
        if not self.account_sid:
            raise ValueError("The account SID argument is empty.")
        elif not self.auth_token:
            raise ValueError("The auth_token argument is empty.")
        elif not self.service_phone_number:
            raise ValueError("The service phone number is empty.")

        try:
            self.client = Client(self.account_sid, self.auth_token)

        except (TwilioException) as error:
            print(error)


    def send_sms(self, sender_phone_number: str, message_body: str):
        self.sender_phone_number = sender_phone_number

        try:
            message = self.client.messages.create(
            to=self.sender_phone_number,
            from_=self.service_phone_number,
            body=message_body
        )

        except TwilioRestException as error:
            print(error)
