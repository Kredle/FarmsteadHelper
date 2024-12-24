from django.urls import path
from .views import register_view, login_view, RegisterView, LoginView, SendOTPView, VerifyOTPView, CheckUserView, confirm_register_view, reset_password_view, ResetPasswordConfirmView, ResetPasswordView, new_password_view

urlpatterns = [
    path('register/', register_view, name='register'),  # HTML форма для реєстрації
    path('login/', login_view, name='login'),  # HTML форма для логіну
    path('api/register/', RegisterView.as_view(), name='register_api'),  # API для реєстрації
    path('api/login/', LoginView.as_view(), name='login_api'),  # API для логіну
    path('api/send-otp/', SendOTPView.as_view(), name='send_otp'),
    path('api/verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('api/check-user/', CheckUserView.as_view(), name='check-user'),
    path('confirm-register/', confirm_register_view, name='confirm_register'),
    path('reset-password/', reset_password_view, name='reset_password'),  # Форма для введення email
    path('api/reset-password-confirm/<str:token>/', ResetPasswordConfirmView.as_view(), name='reset_password_confirm'),  # API підтвердження скидання
    path('reset-password/<str:token>/', new_password_view, name='reset_password_form'),  # Форма для введення нового пароля
    path('api/reset-password/', ResetPasswordView.as_view(), name='reset_password_api'),
]
