from django.conf import settings
from twilio.rest import Client
import numpy as np


class TwilioSMS:
    """ Twilio SMS API Queries """
    def __init__(self):
        account_sid = settings.TWILIO_SID
        auth_token = settings.TWILIO_TOKEN
        self.client = Client(account_sid, auth_token)

    def send_message(self, message):
        """ Send Message to a destination phone number """
        return self.client.messages.create(
            body=message,
            from_=settings.TWILIO_SOURCE,
            to=settings.TWILIO_DESTINATION
        )
