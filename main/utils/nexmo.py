from django.conf import settings
import nexmo


class NexmoSMS:
    """ Twilio SMS API Queries """
    def __init__(self):
        account_key = settings.NEXMO_KEY
        auth_secret = settings.NEXMO_SECRET
        self.client = nexmo.Client(account_key, auth_secret)

    def send_message(self, message):
        """ Send Message to a destination phone number """
        return self.client.send_message({
            'text': message,
            'from': settings.NEXMO_SOURCE,
            'to': settings.NEXMO_DESTINATION
        })
