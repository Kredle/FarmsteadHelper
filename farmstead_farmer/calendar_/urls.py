from django.urls import path
from . import views

urlpatterns = [
    path('api/get_sorts/', views.get_sorts, name='get_sorts'),
    path('calendar/', views.calendar, name='calendar'),
    path('api/get_sort_detail', views.get_sort_details, name='get_sort_details'),
]
