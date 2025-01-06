from django.urls import path
from .views import register_view, login_view, RegisterView, LoginView, SendOTPView, VerifyOTPView, CheckUserView, confirm_register_view, CheckUserPassApi, ResetPasswordApi, reset_password_view, new_password_view, profile_view, UserProfileView, UpdateProfileView, CheckAuthView, UserProfileView, LogoutView, SendResetOTPView, change_username, change_bio, change_password, edit_profile_view, upload_avatar
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),  
    path('api/register/', RegisterView.as_view(), name='register_api'), 
    path('api/login/', LoginView.as_view(), name='login_api'), 
    path('api/send-otp/', SendOTPView.as_view(), name='send_otp'),
    path('api/verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('api/check-user/', CheckUserView.as_view(), name='check-user'),
    path('confirm-register/', confirm_register_view, name='confirm_register'),
    path('api/check-user-pass/', CheckUserPassApi.as_view(), name='check_user_pass'),
    path('api/reset-password/', ResetPasswordApi.as_view(), name='reset_password'),
    path('reset-password/', reset_password_view, name='reset_password_view'),
    path('new-password/', new_password_view, name='new_password'),
    path('profile/<str:username>/', profile_view, name='profile_view'),
    path('api/profile/', UserProfileView.as_view(), name='user_profile'),
    path('api/profile/update/', UpdateProfileView.as_view(), name='update_profile'),
    path('api/check-auth/', CheckAuthView.as_view(), name='CheckAuthView'),
    path('api/user-data/', UserProfileView.as_view(), name='UserProfileView'),
    path('api/logout/', LogoutView.as_view(), name='LogoutView'),
    path('api/send-otp-reset/', SendResetOTPView.as_view(), name ='send_otp_reset'),
    path('api/change-username/', change_username, name='change_username'),
    path('api/change-bio/', change_bio, name='change_bio'),
    path('api/change-password/', change_password, name='change_password'),
    path('edit-profile/', edit_profile_view, name ='edit_profile_view'),
    path('api/upload-avatar/', upload_avatar, name='upload-avatar')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
