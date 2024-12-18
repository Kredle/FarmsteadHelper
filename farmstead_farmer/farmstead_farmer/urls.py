from django.urls import path, include
from feedback.views import feedback_view

urlpatterns = [
    path('', include('api.urls')),
    path('feedback/', feedback_view, name='feedback')
]