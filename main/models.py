from django.db import models


class Record(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    water_level = models.FloatField()
    rainfall_duration = models.FloatField()
    rainfall_intensity = models.FloatField()

    def __str__(self):
        return f"{self.water_level} - {self.date_created}"
