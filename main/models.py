from django.db import models
from main.utils.twilio import TwilioSMS
from main.utils.predictor import States, get_state


class Record(models.Model):
    """ Entry for All Data sent from Sensors """

    date_created = models.DateTimeField(auto_now_add=True)
    water_level = models.FloatField()
    rainfall_duration = models.FloatField()
    rainfall_intensity = models.FloatField()

    def __str__(self):
        return f"{self.water_level} - {self.date_created}"

    @property
    def state(self):
        return get_state(self.water_level)


class Prediction(models.Model):
    """ 
    A History of All Predictions
    """
    STATES = (
        ('N', States.NORMAL),
        ('A', States.ALMOST_FLOODED),
        ('F', States.FLOODED),
    )
    date_created = models.DateTimeField(auto_now_add=True)
    prediction = models.CharField(max_length=1, choices=STATES)
    date_predicted = models.DateTimeField()
    uid = models.UUIDField(editable=False)

    def __str__(self):
        return f"{self.get_prediction_display()} - {self.date_predicted}"

    def is_flood(self):
        return self.get_prediction_display() == States.FLOODED


class Notification(models.Model):
    """ 
    Notification System both Emailing and SMS
    """
    message = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    
    @classmethod
    def send(cls, prediction=None, sms=True):
        message = f"There is an impending Flood at {prediction.date_predicted.strftime('%D %H:%M:%S')}"
        notification = cls.objects.create(message=message)
        # TODO Send Email
        if sms:
            twilio = TwilioSMS()
            twilio.send_message(notification.message)

