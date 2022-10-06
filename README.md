# GT Calendar SMS

This Flask application sends an SMS message with a list of the 3 next available time slots in a friend's calendar.

The full usecase should include the following:

1. When triggered by an incoming text message, the app fetches up to 20 of the last scheduled events in Calendly.
2. It then sends an SMS message with the 3 next available times in the calendar:
    * The time slots must be at least 3 hours long.
    * The times slots may not begin earlier than 8 AM ET or later than 10 PM ET.

## TODO

* Configure the SMS service to prompt for a time slot preference.
* Add a new event in Google Calendar for the specified time slot if possible.
* Send a final confirmation SMS to the user.

## Tech Stack

* Python 3.10.6
* Flask 2.2.2
* Google API Python Client 2.64.0
* PyCalendly 1.0.0
* PyNgrok 5.1.0
* Twilio 7.14.1
* Twilio CLI (Powershell) 5.0.0
