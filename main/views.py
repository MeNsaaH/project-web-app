import json
from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework import viewsets

from main.models import Record
from main.serializers import RecordSerializer

class Index(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['water_level']  = json.dumps(list(reversed(
            Record.objects.values_list('water_level', flat=True).order_by('-id')[:12])))
        context['rainfall']  = Record.objects.values_list('rainfall_intensity', flat=True)
        return context


# ViewSets define the view behavior.
class RecordViewSet(viewsets.ModelViewSet):
    queryset = Record.objects.all()
    serializer_class = RecordSerializer 

