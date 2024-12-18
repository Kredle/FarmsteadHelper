from django.urls import path
from .views import register_view, login_view, RegisterView, LoginView

urlpatterns = [
    path('register/', register_view, name='register'),  # HTML форма для реєстрації
    path('login/', login_view, name='login'),  # HTML форма для логіну
    path('api/register/', RegisterView.as_view(), name='register_api'),  # API для реєстрації
    path('api/login/', LoginView.as_view(), name='login_api'),  # API для логіну
]
