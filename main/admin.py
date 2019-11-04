from django.contrib import admin
from main.models import Record, Prediction, Notification


admin.site.register([Record, Prediction, Notification])

