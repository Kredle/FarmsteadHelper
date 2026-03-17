from django.urls import path

from .views import react_shell

app_name = 'presentation'

urlpatterns = [
    path('', react_shell, name='react-shell'),
]
