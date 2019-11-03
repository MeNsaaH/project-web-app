""" 
Celery Tasks 
"""

from celery import shared_task
from django.conf import settings
from django.utils import timezone


@shared_task
def get_prediction():
    """
    Get hourly prediction and update graphs
    """
    print("getting predictions")
