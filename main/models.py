from django.db import models
from main.utils import TwilioSMS


class Record(models.Model):
    """ Entry for All Data sent from Sensors """

    date_created = models.DateTimeField(auto_now_add=True)
    water_level = models.FloatField()
    rainfall_duration = models.FloatField()
    rainfall_intensity = models.FloatField()

    def __str__(self):
        return f"{self.water_level} - {self.date_created}"


class PredictionHistory(models.Model):
    """ 
    A History of All Predictions
    """
    date_predicted = models.DateTimeField(auto_now_add=True)
    water_level = models.FloatField()
    time_predicted = models.DateTimeField()

    def __str__(self):
        return f"{self.water_level} - {self.date_predicted}"


class Notifications(models.Model):
    """ 
    Notification System both Emailing and SMS
    """
    message = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    
    @classmethod
    def send(cls, prediction=None, sms=False):
        message = f"There is an impending Flood at {prediction.date_predicted}"
        notification = cls.objects.create(message=message)
        # TODO Send Email
        if sms:
            twilio = TwilioSMS()
            twilio.send_message(notification.message)
