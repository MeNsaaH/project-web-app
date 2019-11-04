import json
from django.conf import settings
from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework import viewsets

from main.models import Record, Prediction, Notification
from main.serializers import RecordSerializer
from main.utils.predictor import get_state, get_state_str


class Index(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_obj = Record.objects.last()
        last_hour = current_obj.date_created.hour
        norm_last_hour = last_hour if last_hour <= 12 else last_hour - 12
        # Add in a QuerySet of all the books
        measured_water_level = list(reversed(
            Record.objects.values_list('water_level', flat=True).order_by('-id')[:last_hour]))
        predictions = [get_state_str(x) for x in reversed(
            Prediction.objects.values_list('prediction', flat=True).order_by('-id')[:12])]
        context['measured_water_level'] = json.dumps(measured_water_level)
        context['measured_flood_state'] = json.dumps([get_state(x) for x in measured_water_level])
        context['predictions'] = json.dumps(predictions)
        context['measured_rainfall'] = Record.objects.values_list('rainfall_intensity', flat=True)
        context['time_type'] = 'am' if last_hour <= 12 else 'pm'
        context['next_state'] = predictions[norm_last_hour - 1]
        context['notifications'] = Notification.objects.filter(read=False)[:5]
        context['current_water_level'] = int((current_obj.water_level/settings.DRAIN_HEIGHT) * 100)
        return context


class RecordViewSet(viewsets.ModelViewSet):
    # ViewSets for the Data API
    queryset = Record.objects.all()
    serializer_class = RecordSerializer 

