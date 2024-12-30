from django.urls import path
from .views import register_view, login_view, RegisterView, LoginView, SendOTPView, VerifyOTPView, CheckUserView, confirm_register_view, CheckUserPassApi, ResetPasswordApi, reset_password_view, new_password_view, SendResetOTPView

urlpatterns = [
    path('register/', register_view, name='register'),  # HTML форма для реєстрації
    path('login/', login_view, name='login'),  # HTML форма для логіну
    path('api/register/', RegisterView.as_view(), name='register_api'),  # API для реєстрації
    path('api/login/', LoginView.as_view(), name='login_api'),  # API для логіну
    path('api/send-otp/', SendOTPView.as_view(), name='send_otp'),
    path('api/verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('api/check-user/', CheckUserView.as_view(), name='check-user'),
    path('confirm-register/', confirm_register_view, name='confirm_register'),
    path('api/check-user-pass/', CheckUserPassApi.as_view(), name='check_user_pass'),
    path('api/reset-password/', ResetPasswordApi.as_view(), name='reset_password'),
    path('reset-password/', reset_password_view, name='reset_password_view'),
    path('api/send-reset-otp/', SendResetOTPView.as_view(), name='send_reset_otp'),
    path('new-password/', new_password_view, name='new_password'),
]
