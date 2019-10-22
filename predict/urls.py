"""predict URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from main.views import Index, RecordViewSet
from rest_framework import routers

# API Router
router = routers.DefaultRouter()
router.register(r'data', RecordViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('', Index.as_view(), name="index"),
]
