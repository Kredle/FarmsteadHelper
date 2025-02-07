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
from rest_framework.decorators import api_view
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from rest_framework.exceptions import ValidationError, NotFound
import requests
from django.core.mail import EmailMultiAlternatives

def edit_profile_view(request):
    return render(request, 'profile/edit_profile.html')

@api_view(['POST'])
def check_profile(request):
    token = request.data.get('token')
    username = request.data.get('username')
    
    if not username:
        return Response({'detail': 'Username відсутній'}, status=400)

    if not token:
        return Response({'favorites': []})

    try:
        # Отримуємо користувача по токену
        user_from_token = CustomUser.objects.get(auth_token=token)
    except CustomUser.DoesNotExist:
        return Response({'detail': 'Невірний токен'}, status=400)

    if user_from_token.username != username:
        return Response({'favorites': []})

    try:
        user = CustomUser.objects.get(username=username)
    except CustomUser.DoesNotExist:
        return Response({'detail': 'Користувача не знайдено'}, status=404)

    favorite_items = []
    if user_from_token == user and user.is_favorite_private:
        for item in user.favorites:
            favorite_items.append({
                'common_name': item.get('name', 'Невідомий обʼєкт'),
                'image_url': item.get('image_url', 'default.jpg'),
                'url': item.get('link', '#'),
                'category': item.get('category', 'Без категорії')
            })
    return Response({'favorites': favorite_items})


def profile_view(request, username):
    try:
        user = CustomUser.objects.get(username=username)
    except CustomUser.DoesNotExist:
        return render(request, 'error.html', {'error': 'Користувача не знайдено'})

    favorite_items = []

    if not user.is_favorite_private:
        for item in user.favorites:
            favorite_items.append({
                    'common_name': item.get('name', 'Невідомий обʼєкт'),
                    'image_url': item.get('image_url', 'default.jpg'),
                    'url': item.get('link', '#'),
                    'category': item.get('category', 'Без категорії')
                })

    return render(request, 'profile/view_profile.html', {'user': user, 'favorites': favorite_items, 'is_own_profile': False})





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

# Відповідає за редагування профілю через API
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

class SendOTPView(APIView):
    def post(self, request):
        data = request.data
        email = data.get('email')

        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        otp = generate_otp()
        
        # Збереження OTP в кеші на 10 хвилин
        cache.set(f"otp_{email}", otp, timeout=600)
        
        try:
            # Підготовка листа
            subject = 'Підтвердження реєстрації FarmsteadHelper'
            from_email = 'from@example.com'
            to_email = [email]
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
                        <p>&copy; 2024 FarmsteadHelper. Усі права захищено.</p>
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
            return Response({'error': f'Failed to send email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)



User = get_user_model()

class CheckUserView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email обов’язковий.'}, status=status.HTTP_400_BAD_REQUEST)

        # Використовуємо кастомну модель користувача для перевірки
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Цей логін або email вже використовується.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Email доступний'}, status=status.HTTP_200_OK)

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
                return Response({'message': 'OTP вірний.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Невірний код OTP.'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': f'Помилка на сервері: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# Форма для реєстрації через HTML
def register_view(request):
    if request.method == 'POST':
        data = {
            'username': request.POST.get('username'),
            'email': request.POST.get('email'),
            'firstname': request.POST.get('firstname'),
            'lastname': request.POST.get('lastname'),
            'password': request.POST.get('password'),
            'repeat_password': request.POST.get('repeat_password')
        }
        serializer = RegisterSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            return render(request, 'api/login.html', {'success': 'Успішно зареєстровано. Тепер увійдіть.'})
        else:
            return render(request, 'api/register.html', {'errors': serializer.errors})
    
    return render(request, 'api/register.html')


# Форма для логіну через HTML
def login_view(request):
    if request.method == 'POST':
        data = {
            'username': request.POST.get('username'),
            'password': request.POST.get('password')
        }
        serializer = LoginSerializer(data=data)
        if serializer.is_valid():
            user = serializer.validated_data
            token, _ = Token.objects.get_or_create(user=user)
            return render(request, 'dashboard.html', {'token': token.key})
        else:
            return render(request, 'api/login.html', {'error': 'Невірні дані для входу.'})

    return render(request, 'api/login.html')


# Реєстрація через API для створення токену
class RegisterView(APIView):
    def post(self, request):
        print("Received data:", request.data)
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Логін через API для отримання токену
class LoginView(APIView):
    def post(self, request):
        print("Received data:", request.data)
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def confirm_register_view(request):
    return render(request, 'api/confirm-register.html')

class CheckUserPassApi(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email обов’язковий.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'message': 'Користувача знайдено.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Користувача з таким email не знайдено.'}, status=status.HTTP_404_NOT_FOUND)


from django.contrib.auth.hashers import make_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist

class ResetPasswordApi(APIView):
    def post(self, request):
        try:
            # Отримуємо параметри з запиту
            email = request.data.get('email')
            new_password = request.data.get('new_password')
            confirm_password = request.data.get('confirm_password')

            if not email or not new_password or not confirm_password:
                return Response({'error': 'Усі поля є обов’язковими.'}, status=status.HTTP_400_BAD_REQUEST)

            if len(new_password) < 8:
                return Response({'error': 'Пароль має бути не менше 8 символів .'}, status=status.HTTP_400_BAD_REQUEST)
            if new_password != confirm_password:
                return Response({'error': 'Паролі не співпадають.'}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.filter(email=email).first()

            if not user:
                return Response({'error': 'Користувача з таким email не знайдено.'}, status=status.HTTP_404_NOT_FOUND)

            # Update password
            user.password = make_password(new_password)
            user.save()

            return Response({'message': 'Пароль успішно змінено.'}, status=status.HTTP_200_OK)

        except ObjectDoesNotExist as e:
            # This will catch the specific exception if the user is not found
            return Response({'error': 'Користувача з таким email не знайдено.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # General error handling
            print(f"An error occurred: {e}")
            return Response({'error': 'Сталася помилка. Спробуйте пізніше.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def reset_password_view(request):
    email = request.GET.get('email')

    if request.method == 'GET':
        if email:  
            return render(request, 'api/new_password.html', {'email': email})
        else:  
            return render(request, 'api/reset_password.html')

    elif request.method == 'POST':
        if email: 
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if not new_password or not confirm_password:
                return render(request, 'api/new_password.html', {
                    'error': 'Всі поля є обов’язковими.',
                    'email': email
                })

            if new_password != confirm_password:
                return render(request, 'api/new_password.html', {
                    'error': 'Паролі не співпадають.',
                    'email': email
                })

            user = User.objects.filter(email=email).first()
            if not user:
                return render(request, 'api/new_password.html', {
                    'error': 'Користувача з таким email не знайдено.',
                    'email': email
                })

            user.password = make_password(new_password)
            user.save()

            return render(request, 'api/new_password.html', {
                'success': 'Пароль успішно змінено.',
            })
        else:  # Обробка введення email
            email = request.POST.get('email')
            if not email:
                return render(request, 'api/reset_password.html', {
                    'error': 'Введіть email для відновлення пароля.'
                })

            user = User.objects.filter(email=email).first()
            if not user:
                return render(request, 'api/reset_password.html', {
                    'error': 'Користувача з таким email не знайдено.'
                })

            return render(request, 'api/reset_password.html', {
                'success': 'Інструкції для відновлення пароля надіслані на вашу електронну пошту.'
            })


def new_password_view(request):
    email = request.GET.get('email') 
    return render(request, 'api/new_password.html', {'email': email})


class CheckAuthView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # Тут можна повернути додаткові дані користувача, якщо потрібно
        return Response({"message": "You are authenticated", "username": user.username}, status=status.HTTP_200_OK)

from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.authtoken.models import Token

class UserProfileView(APIView):
    def post(self, request):
        """
        Отримати дані користувача за переданим токеном у тілі запиту.
        """
        token_key = request.data.get('token', None)
        if not token_key:
            raise ValidationError("Токен відсутній у запиті.")

        try:
            token = Token.objects.get(key=token_key)
            user = token.user
        except Token.DoesNotExist:
            raise NotFound("Користувача з таким токеном не знайдено.")

        user.last_activity = timezone.now()
        user.save(update_fields=['last_activity'])

        avatar_url = user.get_avatar_url()

        data = {
            "username": user.username,
            "email": user.email,
            "firstname": user.firstname,
            "lastname": user.lastname,
            "bio": user.bio,
            "favorites": user.favorites,
            "avatarUrl": avatar_url,
            "lastActivity": user.last_activity,
            "dateJoined": user.date_joined,
            "flag" : user.is_favorite_private
        }

        return Response(data, status=200)


class LogoutView(APIView):
    def post(self, request):
        """
        Вихід користувача за переданим токеном у тілі запиту.
        """
        # Витягуємо токен із тіла запиту
        token_key = request.data.get('token', None)
        if not token_key:
            raise ValidationError("Токен відсутній у запиті.")
        
        try:
            # Знаходимо токен у базі даних
            token = Token.objects.get(key=token_key)
            # Видаляємо токен (це виконує фактично вихід користувача)
            token.delete()
            return Response({"detail": "Logged out successfully"}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            raise ValidationError("Невірний токен.")

class SendResetOTPView(APIView):
    def post(self, request):
        data = request.data
        email = data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        otp = generate_otp()
        
        # Збереження OTP в кеші на 10 хвилин
        cache.set(f"otp_{email}", otp, timeout=600)
        
        try:
            # Підготовка листа
            subject = 'Скидання паролю FarmsteadHelper'
            from_email = 'from@example.com'
            to_email = [email]
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
                        <p>&copy; 2024 FarmsteadHelper. Усі права захищено.</p>
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
            return Response({'error': f'Failed to send email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def change_username(request):
    token = request.data.get('token')
    new_username = request.data.get('username')

    if not token or not new_username:
        return Response({'error': 'Token and new username are required'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(auth_token=token).first()
    if not user:
        return Response({'error': 'Неправильний токен'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=new_username).exists():
        return Response({'error': 'Користувач із таким ім’ям уже існує'}, status=status.HTTP_400_BAD_REQUEST)

    if user.last_username_update and timezone.now() - user.last_username_update < timedelta(days=7):
        return Response({'error': 'Ви можете змінити ім\'я користувача раз у 7 днів'}, status=status.HTTP_400_BAD_REQUEST)

    user.username = new_username
    user.last_username_update = timezone.now()
    user.save()

    return Response({'message': 'Username updated successfully'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def change_bio(request):
    token = request.data.get('token')
    new_bio = request.data.get('bio')

    if not token or not new_bio:
        return Response({'error': 'Token and bio are required'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate token and get the user
    user = User.objects.filter(auth_token=token).first()
    if not user:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

    # Update bio
    user.bio = new_bio
    user.save()

    return Response({'message': 'Bio updated successfully'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def change_password(request):
    token = request.data.get('token')
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')

    if not token or not current_password or not new_password or not confirm_password:
        return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

    if new_password != confirm_password:
        return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate token and get the user
    user = User.objects.filter(auth_token=token).first()
    if not user:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the current password is correct
    if not user.check_password(current_password):
        return Response({'error': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

    # Update password
    user.password = make_password(new_password)
    user.save()

    return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def upload_avatar(request):
    token = request.data.get('token')
    avatar = request.FILES.get('avatar')

    if not token or not avatar:
        return Response({'error': 'Token and avatar file are required'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(auth_token=token).first()
    if not user:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

    avatar_path = f"avatars/{user.id}/{avatar.name}"
    try:
        saved_path = default_storage.save(avatar_path, ContentFile(avatar.read()))
        avatar_url = f"{settings.MEDIA_URL}{saved_path}" 
    except Exception as e:
        return Response({'error': f"Failed to save avatar: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    user.avatar = avatar_url
    user.save()

    return Response({'message': 'Avatar uploaded successfully', 'avatar_url': avatar_url}, status=status.HTTP_200_OK)

class UpdateNameView(APIView):
    def post(self, request):
        """
        Оновлення імені та прізвища користувача через токен.
        """
        token_key = request.data.get('token')
        new_firstname = request.data.get('firstname')
        new_lastname = request.data.get('lastname')

        if not token_key:
            raise ValidationError("Токен є обов'язковим.")
        if not new_firstname or not new_lastname:
            raise ValidationError("Ім'я та прізвище обов'язкові для заповнення.")

        try:
            token = Token.objects.get(key=token_key)
            user = token.user
        except Token.DoesNotExist:
            raise NotFound("Користувача з таким токеном не знайдено.")

        user.firstname = new_firstname
        user.lastname = new_lastname
        user.save(update_fields=['firstname', 'lastname'])

        return Response({
            "message": "Ім'я та прізвище успішно оновлені.",
            "firstname": user.firstname,
            "lastname": user.lastname,
        }, status=200)

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
            return Response('Невірний або прострочений OTP', status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response('Користувача з таким email не знайдено', status=status.HTTP_404_NOT_FOUND)

        if not user.check_password(password):
            return Response('Невірний пароль', status=status.HTTP_400_BAD_REQUEST)

        # Видалення акаунту
        user.auth_token.delete()
        user.delete()

        return Response({'message': 'Обліковий запис успішно видалено'}, status=status.HTTP_200_OK)


class SendOTPEmailView(APIView):
    def post(self, request):
        data = request.data
        email = data.get('email')

        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Перевірка, чи існує користувач з таким email
        if User.objects.filter(email=email).exists():
            return Response({'error': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        otp = generate_otp()

        # Зберігаємо OTP у кеш для валідації через 10 хвилин
        cache.set(f"otp_{email}", otp, timeout=600)

        try:
            # Підготовка листа
            subject = 'Підтвердження зміни електронної адреси FarmsteadHelper'
            from_email = 'from@example.com'
            to_email = [email]
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
                        <p>&copy; 2024 FarmsteadHelper. Усі права захищено.</p>
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
            return Response({'error': f'Failed to send email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)


class ChangeEmailView(APIView):
    def post(self, request):
        data = request.data
        token = data.get('token')
        new_email = data.get('email')
        otp = data.get('otp')

        if not token or not new_email or not otp:
            return Response({'error': 'Token, new email, and OTP are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            auth_token = Token.objects.get(key=token)
            user = auth_token.user
        except Token.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=new_email).exists():
            return Response({'error': 'This email is already registered'}, status=status.HTTP_400_BAD_REQUEST)


        cached_otp = cache.get(f"otp_{new_email}")
        if cached_otp != otp:
            return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user.email = new_email
            user.save()
        except Exception as e:
            return Response({'error': f'Failed to update email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'Email updated successfully'}, status=status.HTTP_200_OK)

class SendOTPDeleteView(APIView):
    def post(self, request):
        data = request.data
        email = data.get('email')

        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        otp = generate_otp()
        
        # Збереження OTP в кеші на 10 хвилин
        cache.set(f"otp_{email}", otp, timeout=600)
        
        try:
            # Підготовка листа
            subject = 'Запит на видалення акаунту FarmsteadHelper'
            from_email = 'from@example.com'
            to_email = [email]
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
                        <p>&copy; 2024 FarmsteadHelper. Усі права захищено.</p>
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
            return Response({'error': f'Failed to send email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)

User = get_user_model()

@api_view(['POST'])
def toggle_favorite(request):
    data = request.data

    token = data.get('token')
    if not token:
        return Response({'error': 'Токен не надано.'}, status=400)

    try:
        user = Token.objects.get(key=token).user
    except Token.DoesNotExist:
        return Response({'error': 'Недійсний токен.'}, status=403)

    required_fields = ['name', 'link', 'category']
    if not all(field in data for field in required_fields):
        return Response({'error': 'Відсутні необхідні дані.'}, status=400)

    favorite_item = {
        'name': data['name'],
        'image_url': data.get('image_url'),
        'link': data['link'],
        'category': data['category']
    }

    if favorite_item in user.favorites:
        user.favorites.remove(favorite_item)
        action = 'removed'
    else:
        user.favorites.append(favorite_item)
        action = 'added'

    user.save()
    return Response({'status': action, 'favorites': user.favorites})

@api_view(['POST'])
def check_favorite(request):
    data = request.data

    # Отримуємо токен
    token = data.get('token')
    if not token:
        return Response({'error': 'Токен не надано.'}, status=400)

    # Перевірка на дійсність токену
    try:
        user = Token.objects.get(key=token).user
    except Token.DoesNotExist:
        return Response({'error': 'Недійсний токен.'}, status=403)

    # Перевіряємо, чи є всі необхідні дані
    required_fields = ['name', 'link', 'category']
    if not all(field in data for field in required_fields):
        return Response({'error': 'Відсутні необхідні дані.'}, status=400)

    favorite_item = {
        'name': data['name'],
        'image_url': data.get('image_url'),
        'link': data['link'],
        'category': data['category']
    }

    if favorite_item in user.favorites:
        action = 'inside'
    else:
        action = 'not inside'
    return Response({'status': action})

@api_view(['POST'])
def is_favorite_private_change(request):
    token = request.data.get('token')

    if not token:
        return Response({'detail': 'Неправильний токен'}, status=400)
    try:
        user = CustomUser.objects.get(auth_token=token)
    except CustomUser.DoesNotExist:
        return Response({'detail': 'Невірний токен'}, status=400)
    
    if user.is_favorite_private:
        user.is_favorite_private = 0
        user.save()
        return Response({'status':'Статус змінено на 0'})
    else:
        user.is_favorite_private = 1
        user.save()
        return Response({'status':'Статус змінено на 1'})
    
    
