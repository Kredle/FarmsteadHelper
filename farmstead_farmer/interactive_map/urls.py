from django.urls import path
from .views import map_overview

urlpatterns = [
    path('', map_overview, name='map_overview'),
]
