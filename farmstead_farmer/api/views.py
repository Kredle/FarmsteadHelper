from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .serializers import RegisterSerializer, LoginSerializer, UserProfileSerializer
from django.shortcuts import render, redirect
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
import random
import logging
from .models import OTP
from django.core.cache import cache
from django.contrib.auth import get_user_model
from .forms import ProfileUpdateForm
from django.contrib.auth.decorators import login_required
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import AnonymousUser
from .models import CustomUser
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_protect
from .forms import ProfileUpdateForm
import json
from django.http import JsonResponse
from datetime import timedelta
from django.utils import timezone
from rest_framework.decorators import api_view, throttle_classes
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from rest_framework.exceptions import ValidationError, NotFound
import requests
from django.core.mail import EmailMultiAlternatives
from forum.models import Topic, Comment
import pytz
from datetime import datetime
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now
from django.urls import reverse
from api.throttles import SendOTPThrottle, BasicThrottle, UpdateData, MainAPiThrottle, DataScraptingTrottle
from core.application.auth import AuthUseCase
from core.application.favorites import FavoriteUseCase
from core.application.forum import ForumUseCase
from core.application.profile import ProfileUseCase
from core.domain.exceptions import InvalidTokenError, MissingFieldError, UserNotFoundError
from core.infrastructure.forum_repositories import DjangoForumRepository
from core.infrastructure.repositories import DjangoUserRepository

user_repository = DjangoUserRepository()
forum_repository = DjangoForumRepository()
auth_use_case = AuthUseCase(user_repository)
favorite_use_case = FavoriteUseCase(user_repository)
forum_use_case = ForumUseCase(forum_repository, user_repository)
profile_use_case = ProfileUseCase(user_repository)

def edit_profile_view(request):
    return render(request, 'profile/edit_profile.html')

@api_view(['POST'])
@throttle_classes([UpdateData])
def is_map_private_change(request):
    try:
        payload = profile_use_case.toggle_map_private(request.data.get('token'))
        return Response(payload)
    except InvalidTokenError as error:
        return Response({'detail': str(error)}, status=400)

@api_view(['POST'])
@throttle_classes([MainAPiThrottle])
def check_profile(request):
    try:
        payload = profile_use_case.check_profile(
            token=request.data.get('token'),
            username=request.data.get('username'),
        )
        return Response(payload)
    except MissingFieldError as error:
        return Response({'detail': str(error)}, status=400)
    except InvalidTokenError as error:
        return Response({'detail': str(error)}, status=400)
    except UserNotFoundError as error:
        return Response({'detail': str(error)}, status=404)

@throttle_classes([MainAPiThrottle])
def update_author_name(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            old_name = data.get('oldName')
            new_name = data.get('newName')

            forum_use_case.update_author_name(old_name, new_name)

            return JsonResponse({'status': 'success', 'message': 'Ім\'я автора оновлено успішно в topics та comments'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Неправильний метод запиту'}, status=405)

@throttle_classes([MainAPiThrottle])
def profile_view(request, username):
    viewed_user = user_repository.get_by_username(username)
    if viewed_user is None:
        return redirect('/')
    favorites = getattr(viewed_user, 'favorites', []) or []
    return render(request, 'profile/view_profile.html', {
        'user': viewed_user,
        'favorites': favorites,
    })






@throttle_classes([BasicThrottle])
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Профіль успішно оновлено!'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@throttle_classes([BasicThrottle])
class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Профіль оновлений!'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def generate_otp(length=6):
    """Генерує одноразовий пароль (OTP) заданої довжини."""
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

@throttle_classes([SendOTPThrottle])
class SendOTPView(APIView):
    def post(self, request):
        data = request.data
        email = data.get('email')

        if not email:
            return Response({'error': 'Email є обов\'язковим'}, status=status.HTTP_400_BAD_REQUEST)

        otp = generate_otp()

        # Збереження OTP в кеші на 10 хвилин
        cache.set(f"otp_{email}", otp, timeout=600)

        try:
            # Підготовка листа
            subject = 'Підтвердження реєстрації FarmsteadHelper'
            from_email = 'algowizzards.farmsteadhelper@gmail.com'
            to_email = [email]
            current_year = datetime.now().year
            html_content = f"""
            <!DOCTYPE html>
            <html lang="uk">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Підтвердження реєстрації FarmsteadHelper</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #f6f5cb;
                        margin: 0;
                        padding: 0;
                        color: #333;
                    }}
                    .email-container {{
                        max-width: 600px;
                        margin: 30px auto;
                        padding: 20px;
                        background-color: #f6f5cb;
                        border-radius: 8px;
                        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                    }}
                    .email-container h2 {{
                        font-size: 24px;
                        color: #28a745;
                        text-align: center;
                        margin-top: 20px;
                        font-weight: bold;
                    }}
                    .email-body {{
                        font-size: 16px;
                        line-height: 1.6;
                    }}
                    .email-body p {{
                        margin-bottom: 15px;
                    }}
                    .email-footer {{
                        text-align: center;
                        font-size: 14px;
                        color: #777;
                        margin-top: 30px;
                    }}
                    .otp-code {{
                        text-align: center;
                        font-weight: bold;
                        color: #28a745;
                        font-size: 20px;
                    }}
                </style>
            </head>
            <body>
                <div class="email-container">
                        <div class="email-body">
                            <h2>Вітаємо!</h2>
                            <p>Дякуємо, що обрали платформу <strong>FarmsteadHelper</strong> для ваших потреб! Ми раді вітати вас серед наших користувачів.</p>
                            <p>
                                Ви надіслали запит на реєстрацію, і для підтвердження вашої електронної адреси необхідно ввести OTP код. Це допоможе нам переконатися, що доступ до вашого облікового запису буде безпечним і надійним.
                            </p>
                            <p>
                                Ваш OTP код (дійсний протягом 10 хвилин):
                                <br><h3 class="otp-code" style="text-align: center;">{otp}</h3>
                            </p>
                            <p>
                                Будь ласка, введіть цей код у відповідне поле на сторінці підтвердження реєстрації. Якщо ви не завершуєте реєстрацію протягом 10 хвилин, код стане недійсним, і вам потрібно буде повторити запит.
                            </p>
                            <p>
                                Якщо ви не ініціювали цей запит, не хвилюйтеся — ваш обліковий запис залишається у безпеці. Просто проігноруйте цей лист, і ніяких подальших дій не потрібно.
                                Ми завжди готові допомогти! Якщо у вас виникли будь-які питання чи труднощі з процесом реєстрації, будь ласка, зв’яжіться з нашою командою через форму зворотного зв’язку.
                            </p>
                            <p>Будь ласка, не відповідайте на даний лист повідомленням, надсилання коду проводиться автоматично.</p>
                            <p>З найкращими побажаннями,<br>Команда <strong>FarmsteadHelper</strong></p>
                        </div>
                    <div class="email-footer">
                        <p>&copy; {current_year} FarmsteadHelper. Усі права захищено.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Створення HTML-листа
            msg = EmailMultiAlternatives(subject=subject, from_email=from_email, to=to_email)
            msg.attach_alternative(html_content, "text/html")
            msg.send()

        except Exception as e:
            return Response({'error': f'Невдалося надіслати на email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'OTP успішно надіслано'}, status=status.HTTP_200_OK)



User = get_user_model()
@throttle_classes([BasicThrottle])
class CheckUserView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email обов’язковий.'}, status=status.HTTP_400_BAD_REQUEST)

        if user_repository.email_exists(email):
            return Response({'error': 'Цей логін або email вже використовується.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Email доступний'}, status=status.HTTP_200_OK)

@throttle_classes([SendOTPThrottle])
class VerifyOTPView(APIView):
    def post(self, request):
        otp_code = request.data.get('otp')
        email = request.data.get('email')

        if not otp_code or not email:
            return Response({'error': 'OTP і email обов’язкові.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cached_otp = cache.get(f"otp_{email}")
            if not cached_otp:
                return Response({'error': 'Код OTP не знайдений або термін дії минув.'}, status=status.HTTP_400_BAD_REQUEST)

            if cached_otp == otp_code:
                cache.delete(f"otp_{email}")
                return Response({'message': 'OTP правильний.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Неправильний код OTP.'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': f'Помилка на сервері: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# Форма для реєстрації через HTML
@throttle_classes([BasicThrottle])
def register_view(request): #HERE add otp checking
    return render(request, 'api/register.html')


# Форма для логіну через HTML
@throttle_classes([BasicThrottle])
def login_view(request):
    return render(request, 'api/login.html')


# Реєстрація через API для створення токену
@throttle_classes([BasicThrottle])
class RegisterView(APIView):
    def post(self, request):
        print("Received data:", request.data)
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = auth_use_case.issue_token(user)
            return Response({"token": token}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Логін через API для отримання токену
@throttle_classes([BasicThrottle])
class LoginView(APIView):
    def post(self, request):
        print("Received data:", request.data)
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            token = auth_use_case.issue_token(user)
            return Response({"token": token}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def confirm_register_view(request):
    return render(request, 'api/confirm-register.html')

@throttle_classes([BasicThrottle])
class CheckUserPassApi(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email обов’язковий.'}, status=status.HTTP_400_BAD_REQUEST)

        if auth_use_case.check_user_email_exists(email):
            return Response({'message': 'Користувача знайдено.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Користувача з таким email не знайдено.'}, status=status.HTTP_404_NOT_FOUND)

@throttle_classes([UpdateData])
class ResetPasswordApi(APIView):
    def post(self, request):
        try:
            email = request.data.get('email')
            new_password = request.data.get('new_password')
            confirm_password = request.data.get('confirm_password')

            auth_use_case.reset_password(email, new_password, confirm_password)
            return Response({'message': 'Пароль успішно змінено.'}, status=status.HTTP_200_OK)
        except UserNotFoundError:
            return Response({'error': 'Користувача з таким email не знайдено.'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as error:
            return Response({'error': str(error)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"An error occurred: {e}")
            return Response({'error': 'Сталася помилка. Спробуйте пізніше.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@throttle_classes([BasicThrottle])
def reset_password_view(request):
    return render(request, 'api/reset_password.html')


def new_password_view(request):
    return render(request, 'api/new_password.html')

@throttle_classes([BasicThrottle])
class CheckAuthView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({"message": "Ви є аунтифікованими", "username": user.username}, status=status.HTTP_200_OK)

@throttle_classes([DataScraptingTrottle])
class UserProfileView(APIView):
    def post(self, request):
        token_key = request.data.get('token', None)
        if not token_key:
            raise ValidationError("Токен відсутній у запиті.")

        try:
            data = auth_use_case.get_profile_by_token(token_key)
        except InvalidTokenError:
            raise NotFound("Користувача з таким токеном не знайдено.")

        return Response(data, status=200)

@throttle_classes([UpdateData])
class LogoutView(APIView):
    def post(self, request):
        token_key = request.data.get('token', None)
        if not token_key:
            raise ValidationError("Токен відсутній у запиті.")

        try:
            auth_use_case.logout(token_key)
            return Response({"detail": "Ви успішно вийшли з облікового запису"}, status=status.HTTP_200_OK)
        except InvalidTokenError:
            raise ValidationError("Неправильний токен.")

@throttle_classes([SendOTPThrottle])
class SendResetOTPView(APIView):
    def post(self, request):
        data = request.data
        email = data.get('email')
        if not email:
            return Response({'error': 'Email є обов\'язковим'}, status=status.HTTP_400_BAD_REQUEST)

        otp = generate_otp()

        # Збереження OTP в кеші на 10 хвилин
        cache.set(f"otp_{email}", otp, timeout=600)

        try:
            # Підготовка листа
            subject = 'Скидання паролю FarmsteadHelper'
            from_email = 'algowizzards.farmsteadhelper@gmail.com'
            to_email = [email]
            current_year = datetime.now().year
            html_content = f"""
            <!DOCTYPE html>
            <html lang="uk">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Скидання паролю FarmsteadHelper</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #f7cfdb;
                        margin: 0;
                        padding: 0;
                        color: #333;
                    }}
                    .email-container {{
                        max-width: 600px;
                        margin: 30px auto;
                        padding: 20px;
                        background-color: #f7cfdb;
                        border-radius: 8px;
                        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                    }}
                    .email-container h2 {{
                        font-size: 24px;
                        color: #28a745;
                        text-align: center;
                        margin-top: 20px;
                        font-weight: bold;
                    }}
                    .email-body {{
                        font-size: 16px;
                        line-height: 1.6;
                    }}
                    .email-body p {{
                        margin-bottom: 15px;
                    }}
                    .email-footer {{
                        text-align: center;
                        font-size: 14px;
                        color: #777;
                        margin-top: 30px;
                    }}
                    .otp-code {{
                        text-align: center;
                        font-weight: bold;
                        color: #28a745;
                        font-size: 20px;
                    }}
                </style>
            </head>
            <body>
                <div class="email-container">
                        <div class="email-body">
                            <h2>Вітаємо!</h2>
                            <p>Ми раді, що Ви є користувачем <strong>FarmsteadHelper</strong>. </p>
                            <p>
                                Ви надіслали запит на скидання паролю, і для підтвердження цієї дії необхідно ввести OTP код. Це допоможе нам переконатися, що доступ до вашого облікового запису буде безпечним і надійним.
                            </p>
                            <p>
                                Ваш OTP код (дійсний протягом 10 хвилин):
                                <br><h3 class="otp-code" style="text-align: center;">{otp}</h3>
                            </p>
                            <p>
                                Будь ласка, введіть цей код у відповідне поле на сторінці скидання паролю. Якщо ви не встигнете виконати дії протягом 10 хвилин, код стане недійсним, і вам потрібно буде повторити запит.
                            </p>
                            <p>
                                Якщо ви не ініціювали цей запит, не хвилюйтеся — ваш обліковий запис залишається у безпеці. Просто проігноруйте цей лист, і ніяких подальших дій не потрібно.
                            </p>
                            <p>
                                Ми завжди готові допомогти! Якщо у вас виникли будь-які питання чи труднощі з процесом скидання паролю, будь ласка, зв’яжіться з нашою командою через форму зворотного зв’язку.
                            </p>
                            <p>Будь ласка, не відповідайте на даний лист повідомленням, надсилання коду проводиться автоматично.</p>
                            <p>З найкращими побажаннями,<br>Команда <strong>FarmsteadHelper</strong></p>
                        </div>
                    <div class="email-footer">
                        <p>&copy; {current_year} FarmsteadHelper. Усі права захищено.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            # Створення HTML-листа
            msg = EmailMultiAlternatives(subject=subject, from_email=from_email, to=to_email)
            msg.attach_alternative(html_content, "text/html")
            msg.send()

        except Exception as e:
            return Response({'error': f'Не вдалося надіслати на email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'OTP успішно надіслано'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@throttle_classes([UpdateData])
def change_username(request):
    token = request.data.get('token')
    new_username = request.data.get('username')
    try:
        auth_use_case.change_username(token, new_username)
        return Response({'message': 'Username успішно оновлено'}, status=status.HTTP_200_OK)
    except InvalidTokenError:
        return Response({'error': 'Неправильний токен'}, status=status.HTTP_400_BAD_REQUEST)
    except ValueError as error:
        return Response({'error': str(error)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@throttle_classes([UpdateData])
def change_bio(request):
    token = request.data.get('token')
    new_bio = request.data.get('bio')
    try:
        auth_use_case.change_bio(token, new_bio)
        return Response({'message': 'Біо змінено'}, status=status.HTTP_200_OK)
    except InvalidTokenError:
        return Response({'error': 'Недійсний токен'}, status=status.HTTP_400_BAD_REQUEST)
    except ValueError as error:
        return Response({'error': str(error)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@throttle_classes([UpdateData])
def change_password(request):
    token = request.data.get('token')
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')
    try:
        auth_use_case.change_password(token, current_password, new_password, confirm_password)
        return Response({'message': 'Пароль успішно змінено'}, status=status.HTTP_200_OK)
    except InvalidTokenError:
        return Response({'error': 'Недійсний токен'}, status=status.HTTP_400_BAD_REQUEST)
    except ValueError as error:
        return Response({'error': str(error)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@throttle_classes([UpdateData])
def upload_avatar(request):
    token = request.data.get('token')
    avatar = request.FILES.get('avatar')

    if not token or not avatar:
        return Response({'error': 'Token та avatar файл є обов\'язковими'}, status=status.HTTP_400_BAD_REQUEST)

    user = user_repository.find_by_token(token)
    if not user:
        return Response({'error': 'Недійсний токен'}, status=status.HTTP_400_BAD_REQUEST)

    avatar_path = f"avatars/{user.id}/{avatar.name}"
    try:
        saved_path = default_storage.save(avatar_path, ContentFile(avatar.read()))
        avatar_url = f"{settings.MEDIA_URL}{saved_path}"
    except Exception as e:
        return Response({'error': f"Не вдалося зберегти avatar: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    auth_use_case.update_avatar(token, avatar_url)

    return Response({'message': 'Avatar успішно оновлено', 'avatar_url': avatar_url}, status=status.HTTP_200_OK)

@throttle_classes([UpdateData])
class UpdateNameView(APIView):
    def post(self, request):
        token_key = request.data.get('token')
        new_firstname = request.data.get('firstname')
        new_lastname = request.data.get('lastname')

        if not token_key:
            raise ValidationError("Токен є обов'язковим.")
        if not new_firstname or not new_lastname:
            raise ValidationError("Ім'я та прізвище обов'язкові для заповнення.")

        try:
            firstname, lastname = auth_use_case.update_name(token_key, new_firstname, new_lastname)
        except InvalidTokenError:
            raise NotFound("Користувача з таким токеном не знайдено.")

        return Response({
            "message": "Ім'я та прізвище успішно оновлені.",
            "firstname": firstname,
            "lastname": lastname,
        }, status=200)

@throttle_classes([UpdateData])
class DeleteAccountView(APIView):
    def post(self, request):
        data = request.data

        email = data.get('email')
        otp = data.get('otp')
        password = data.get('password')
        captcha_token = data.get('captcha_token')

        if not email or not otp or not password or not captcha_token:
            return Response({'error': 'Всі поля є обов’язковими: email, OTP, пароль, і токен капчі'}, status=status.HTTP_400_BAD_REQUEST)

        # Перевірка reCAPTCHA
        captcha_secret = "6Lct-rEqAAAAAIzeO0FW9UMFwbuveyCzBgavSTwj"
        captcha_url = "https://www.google.com/recaptcha/api/siteverify"
        captcha_response = requests.post(captcha_url, data={'secret': captcha_secret, 'response': captcha_token})
        captcha_result = captcha_response.json()

        if not captcha_result.get("success", False):
            return Response('Час дії капчі вичерпано', status=status.HTTP_400_BAD_REQUEST)

        cached_otp = cache.get(f"otp_{email}")
        if not cached_otp or cached_otp != otp:
            return Response('Неправильний або прострочений OTP', status=status.HTTP_400_BAD_REQUEST)

        try:
            auth_use_case.delete_account(email, password)
        except UserNotFoundError:
            return Response('Користувача з таким email не знайдено', status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response('Неправильний пароль', status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Обліковий запис успішно видалено'}, status=status.HTTP_200_OK)

@throttle_classes([SendOTPThrottle])
class SendOTPEmailView(APIView):
    def post(self, request):
        data = request.data
        email = data.get('email')

        if not email:
            return Response({'error': 'Email є обов\'язковим'}, status=status.HTTP_400_BAD_REQUEST)

        if user_repository.email_exists(email):
            return Response({'error': 'Користувач з таким email вже існує'}, status=status.HTTP_400_BAD_REQUEST)

        otp = generate_otp()

        # Зберігаємо OTP у кеш для валідації через 10 хвилин
        cache.set(f"otp_{email}", otp, timeout=600)

        try:
            # Підготовка листа
            subject = 'Підтвердження зміни електронної адреси FarmsteadHelper'
            from_email = 'algowizzards.farmsteadhelper@gmail.com'
            to_email = [email]
            current_year = datetime.now().year
            html_content = f"""
            <!DOCTYPE html>
            <html lang="uk">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Запит на зміну електронної пошти</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #f6f5cb;
                        margin: 0;
                        padding: 0;
                        color: #333;
                    }}
                    .email-container {{
                        max-width: 600px;
                        margin: 30px auto;
                        padding: 20px;
                        background-color: #f6f5cb;
                        border-radius: 8px;
                        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                    }}
                    .email-container h2 {{
                        font-size: 24px;
                        color: #367557;
                        text-align: center;
                        margin-top: 20px;
                        font-weight: bold;
                    }}
                    .email-body {{
                        font-size: 16px;
                        line-height: 1.6;
                    }}
                    .email-body p {{
                        margin-bottom: 15px;
                    }}
                    .email-footer {{
                        text-align: center;
                        font-size: 14px;
                        color: #777;
                        margin-top: 30px;
                    }}
                    .warning {{
                        font-weight: bold;
                        color: #ff8000;
                    }}
                    .otp-code {{
                        text-align: center;
                        font-weight: bold;
                        color: #007bff;
                        font-size: 20px;
                    }}
                </style>
            </head>
            <body>
                <div class="email-container">
                    <div class="email-body">
                        <h2>Запит на зміну електронної пошти</h2>
                        <p>Ви подали запит на зміну електронної пошти, пов’язаної з вашим акаунтом у <strong>FarmsteadHelper</strong>. Для підтвердження цієї дії вам потрібно ввести код OTP, наведений нижче:</p>
                        <p>
                            Ваш OTP код (дійсний протягом 10 хвилин):
                            <br><h3 class="otp-code">{otp}</h3>
                        </p>
                        <p>Після введення цього коду, ваша електронна пошта буде змінена. Усі майбутні повідомлення, включаючи важливі сповіщення, будуть надсилатися на нову адресу.</p>
                        <p class="warning">
                            Зверніть увагу! Ви несете повну відповідальність за коректність нової електронної пошти. Команда <strong>FarmsteadHelper</strong> не несе відповідальності за будь-які наслідки, пов’язані з помилками під час введення нової адреси, втратою доступу до неї або ненадійністю її захисту.
                        </p>
                        <p>
                            Ми рекомендуємо перевірити всі дані перед завершенням процесу зміни електронної пошти. У разі виникнення питань, наша команда підтримки завжди готова допомогти.
                        </p>
                        <p>Дякуємо, що користуєтеся <strong>FarmsteadHelper</strong>!</p>
                    </div>
                    <div class="email-footer">
                        <p>&copy; {current_year} FarmsteadHelper. Усі права захищено.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Створення HTML-листа
            msg = EmailMultiAlternatives(subject=subject, from_email=from_email, to=to_email)
            msg.attach_alternative(html_content, "text/html")
            msg.send()

        except Exception as e:
            return Response({'error': f'Не вдалося надіслати на email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'OTP успішно надіслано'}, status=status.HTTP_200_OK)

@throttle_classes([UpdateData])
class ChangeEmailView(APIView):
    def post(self, request):
        data = request.data
        token = data.get('token')
        new_email = data.get('email')
        otp = data.get('otp')

        if not token or not new_email or not otp:
            return Response({'error': 'Token, новий email, та OTP є обов\'язковими'}, status=status.HTTP_400_BAD_REQUEST)

        if user_repository.email_exists(new_email):
            return Response({'error': 'Цей email вже є зареєстрованим'}, status=status.HTTP_400_BAD_REQUEST)


        cached_otp = cache.get(f"otp_{new_email}")
        if cached_otp != otp:
            return Response({'error': 'Неправильний або прострочений OTP'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            auth_use_case.change_email(token, new_email)
        except InvalidTokenError:
            return Response({'error': 'Недійсний токен'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Не вдалося надіслати на емейл: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'Email успішно оновлено'}, status=status.HTTP_200_OK)

@throttle_classes([SendOTPThrottle])
class SendOTPDeleteView(APIView):
    def post(self, request):
        data = request.data
        email = data.get('email')

        if not email:
            return Response({'error': 'Email є обов\'язковим'}, status=status.HTTP_400_BAD_REQUEST)

        otp = generate_otp()

        # Збереження OTP в кеші на 10 хвилин
        cache.set(f"otp_{email}", otp, timeout=600)

        try:
            # Підготовка листа
            subject = 'Запит на видалення акаунту FarmsteadHelper'
            from_email = 'algowizzards.farmsteadhelper@gmail.com'
            to_email = [email]
            current_year = datetime.now().year
            html_content = f"""
            <!DOCTYPE html>
            <html lang="uk">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Запит на видалення акаунту FarmsteadHelper</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #f7cfdb;
                        margin: 0;
                        padding: 0;
                        color: #333;
                    }}
                    .email-container {{
                        max-width: 600px;
                        margin: 30px auto;
                        padding: 20px;
                        background-color: #f7cfdb;
                        border-radius: 8px;
                        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                    }}
                    .email-container h2 {{
                        font-size: 24px;
                        color: #d9534f;
                        text-align: center;
                        margin-top: 20px;
                        font-weight: bold;
                    }}
                    .email-body {{
                        font-size: 16px;
                        line-height: 1.6;
                    }}
                    .email-body p {{
                        margin-bottom: 15px;
                    }}
                    .email-footer {{
                        text-align: center;
                        font-size: 14px;
                        color: #777;
                        margin-top: 30px;
                    }}
                    .otp-code {{
                        text-align: center;
                        font-weight: bold;
                        color: #d9534f;
                        font-size: 20px;
                    }}
                </style>
            </head>
            <body>
                <div class="email-container">
                    <div class="email-body">
                        <h2>Запит на видалення акаунту</h2>
                        <p>Доброго дня!</p>
                        <p>Ви надіслали запит на видалення свого акаунту в <strong>FarmsteadHelper</strong>. Ми розуміємо, що прийняття цього рішення могло бути непростим, і шкодуємо, що ви вирішили припинити використання нашого сервісу.</p>
                        <p>
                            Для підтвердження вашого запиту, будь ласка, введіть наступний код OTP:
                            <br><h3 class="otp-code">{otp}</h3>
                        </p>
                        <p>Код дійсний протягом 10 хвилин. Після завершення цього періоду він стане недійсним, і вам доведеться надіслати новий запит на видалення акаунту.</p>
                        <p>Ми хотіли б зазначити, що після підтвердження видалення:</p>
                        <ul>
                            <li>Вся інформація про ваш акаунт буде безповоротно видалена.</li>
                            <li>Доступ до ваших персоналізованих даних та історії буде втрачено.</li>
                            <li>Відновлення акаунту буде неможливим.</li>
                        </ul>
                        <p>Якщо у вас є якісь невирішені питання або ви зіткнулися з труднощами, ми завжди готові допомогти. Ви можете зв’язатися з нашою командою підтримки через форму зворотного зв’язку.</p>
                        <p>Якщо цей запит був зроблений помилково або ви передумали, просто проігноруйте цей лист. Ваш акаунт залишиться без змін.</p>
                        <p>Ми дякуємо вам за використання <strong>FarmsteadHelper</strong> та сподіваємося, що ви повернетесь у майбутньому. Ваші відгуки та пропозиції завжди вітаються — вони допомагають нам ставати краще.</p>
                        <p>Будь ласка, не відповідайте на цей лист, оскільки він був надісланий автоматичною системою.</p>
                        <p>З найкращими побажаннями,<br>Команда <strong>FarmsteadHelper</strong></p>
                    </div>
                    <div class="email-footer">
                        <p>&copy; {current_year} FarmsteadHelper. Усі права захищено.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Створення HTML-листа
            msg = EmailMultiAlternatives(subject=subject, from_email=from_email, to=to_email)
            msg.attach_alternative(html_content, "text/html")
            msg.send()

        except Exception as e:
            return Response({'error': f'Не вдалося надіслати на email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'OTP успішно надіслано'}, status=status.HTTP_200_OK)

User = get_user_model()

@api_view(['POST'])
@throttle_classes([UpdateData])
def toggle_favorite(request):
    try:
        payload = favorite_use_case.toggle(request.data.get('token'), request.data)
        return Response(payload)
    except MissingFieldError as error:
        return Response({'error': str(error)}, status=400)
    except InvalidTokenError as error:
        return Response({'error': str(error)}, status=403)

@api_view(['POST'])
@throttle_classes([UpdateData])
def check_favorite(request):
    try:
        payload = favorite_use_case.check(request.data.get('token'), request.data)
        return Response(payload)
    except MissingFieldError as error:
        return Response({'error': str(error)}, status=400)
    except InvalidTokenError as error:
        return Response({'error': str(error)}, status=403)

@api_view(['POST'])
@throttle_classes([MainAPiThrottle])
def check_map(request):
    try:
        payload = profile_use_case.check_map_visibility(
            token=request.data.get('token'),
            username=request.data.get('username'),
        )
        return Response(payload)
    except MissingFieldError as error:
        return Response({'detail': str(error)}, status=400)
    except UserNotFoundError as error:
        return Response({'error': str(error)}, status=404)

@api_view(['POST'])
@throttle_classes([UpdateData])
def is_favorite_private_change(request):
    try:
        payload = profile_use_case.toggle_favorite_private(request.data.get('token'))
        return Response(payload)
    except InvalidTokenError as error:
        return Response({'detail': str(error)}, status=400)

@throttle_classes([SendOTPThrottle])
class SendOTPModerationView(APIView):
    def post(self, request):
        data = request.data
        username = data.get('username')

        if not username:
            return Response({'error': 'username є обов\'язковим'}, status=status.HTTP_400_BAD_REQUEST)
        user = user_repository.get_by_username(username)
        if not user:
            return Response({'error': 'Користувача не знайдено'}, status=status.HTTP_404_NOT_FOUND)
        otp = generate_otp()

        cache.set(f"otp_{username}", otp, timeout=600)

        try:
            subject = 'Запит на встановлення модераторства'
            from_email = 'algowizzards.farmsteadhelper@gmail.com'
            to_email = ['gamelag11123@gmail.com']
            current_year = datetime.now().year
            html_content = f"""
            <!DOCTYPE html>
            <html lang="uk">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Запит на видалення акаунту FarmsteadHelper</title>
            </head>
            <body>
                <div class="email-container">
                    <div class="email-body">
                        <h2>Запит на встановлення модераторства</h2>
                        <p>Добрий дня!</p>
                        <p>Користувач {username} подав запит на модераторство</p>
                        <p>
                            Код OTP для підтвердження запиту:
                            <br><h3 class="otp-code">{otp}</h3>
                        </p>
                        <p>Код дійсний протягом 10 хвилин. Після завершення цього періоду він стане недійсним</p>
                    </div>
                    <div class="email-footer">
                        <p>&copy; {current_year} FarmsteadHelper. Усі права захищено.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            msg = EmailMultiAlternatives(subject=subject, from_email=from_email, to=to_email)
            msg.attach_alternative(html_content, "text/html")
            msg.send()

        except Exception as e:
            return Response({'error': f'Не вдалося надіслати на email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'OTP успішно надіслано'}, status=status.HTTP_200_OK)


@throttle_classes([SendOTPThrottle])
class VerifyOTPModerationView(APIView):
    def post(self, request):
        otp_code = request.data.get('otp')
        username = request.data.get('username')

        if not otp_code or not username:
            return Response({'error': 'OTP і username обов’язкові.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cached_otp = cache.get(f"otp_{username}")
            if not cached_otp:
                return Response({'error': 'Код OTP не знайдений або термін дії минув.'}, status=status.HTTP_400_BAD_REQUEST)

            if cached_otp == otp_code:
                cache.delete(f"otp_{username}")
                is_superuser = auth_use_case.toggle_superuser(username)
                if is_superuser:
                    return Response({'message': f'OTP вірний. Тепер {username} є модератором'}, status=status.HTTP_200_OK)
                return Response({'message': f'OTP вірний. Тепер {username} не є модератором'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Невірний код OTP.'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': f'Помилка на сервері: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


User = get_user_model()

@throttle_classes([SendOTPThrottle])
class ReportView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            topic_id = request.data.get('topic_id')
            reason = request.data.get('reason', 'Причина не вказана')

            if not topic_id:
                return Response(
                    {"error": "Необхідно вказати ID теми"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                topic_id = int(topic_id)
            except (ValueError, TypeError):
                return Response(
                    {"error": "ID теми має бути числом"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            admin_emails = [email for email in user_repository.get_superuser_emails() if email]

            if not admin_emails:
                return Response(
                    {"error": "Адміністратори не знайдені"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )

            # Генеруємо посилання на тему з вашим URL шаблоном
            topic_url = request.build_absolute_uri(
                reverse('topic_detail', kwargs={'pk': topic_id}))

            kyiv_tz = pytz.timezone("Europe/Kyiv")
            kyiv_time = timezone.now().astimezone(kyiv_tz)

            send_mail(
                subject=f'[СКАРГА] Тема #{topic_id}',
                message=f"""
                Нова скарга на вміст:

                Тема: #{topic_id}
                Посилання: {topic_url}
                Автор скарги: {request.user.username} (ID: {request.user.id})
                Причина: {reason}
                Час: {kyiv_time}

                Будь ласка, перевірте цю скаргу.
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=admin_emails,
                fail_silently=False,
            )

            return Response(
                {"success": "Скаргу успішно надіслано адміністраторам"},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": f"Помилка сервера: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from forum.models import Comment
from forum.models import Topic
import logging
logger = logging.getLogger(__name__)

class CommentReportAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            logger.info(f"Отримано дані: {request.data}")
            # Валідація даних
            comment_id = request.data.get('comment_id')
            if not comment_id:
                return Response(
                    {"error": "Вкажіть ID коментаря"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                comment = forum_repository.get_comment(int(comment_id))
            except ValueError:
                return Response(
                    {"error": "Невірний ID коментаря"},
                    status=status.HTTP_404_NOT_FOUND
                )
            if not comment:
                return Response(
                    {"error": "Невірний ID коментаря"},
                    status=status.HTTP_404_NOT_FOUND
                )

            author_name = comment['Author']
            
            user = user_repository.get_by_username(author_name)
            author_display = user.username if user else 'Анонім'
            topic_title = forum_repository.get_topic_title(comment['Topics_id']) or 'Тема видалена'
            
            kyiv_tz = pytz.timezone("Europe/Kyiv")
            kyiv_time = timezone.now().astimezone(kyiv_tz)
            admin_emails = [email for email in user_repository.get_superuser_emails() if email]
            message = f"""
            Нова скарга на коментар #{comment['id']}
            
            Автор коментаря: {author_display}
            Тема: {topic_title}
            Час: {comment['Date']} {comment['Time']}
            
            Автор скарги: {request.user.username} (ID: {request.user.id})
            Надіслано о {kyiv_time}
            Причина: {request.data.get('reason', 'Не вказано')}
            Посилання: {request.build_absolute_uri(comment['absolute_url'])}
            
            """
            send_mail(
                subject=f"Скарга на коментар #{comment['id']}",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=admin_emails,
                fail_silently=False
            )

            return Response({'success': 'Скаргу надіслано'}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.critical(f"Критична помилка: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
