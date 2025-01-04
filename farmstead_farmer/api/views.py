from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .serializers import RegisterSerializer, LoginSerializer
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

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile_view', username=request.user.username)
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'profile/edit_profile.html', {'form': form})
    
# Головна сторінка та профіль користувача
def profile_view(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(request, 'error.html', {'error': 'Користувача не знайдено'})

    if request.user == user:
        return render(request, 'profile/edit_profile.html', {'user': user})
    else:
        return render(request, 'profile/view_profile.html', {'user': user})


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

        # Use the model method to get the avatar URL without the '/media/' part
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