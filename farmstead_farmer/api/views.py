from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .serializers import RegisterSerializer, LoginSerializer
from django.shortcuts import render
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
            # Перевірка OTP в кеші
            cached_otp = cache.get(f"otp_{email}")
            if not cached_otp:
                return Response({'error': 'Код OTP не знайдений або термін дії минув.'}, status=status.HTTP_400_BAD_REQUEST)

            if cached_otp == otp_code:
                cache.delete(f"otp_{email}")
                # Інші операції, наприклад, реєстрація користувача
                return Response({'message': 'OTP вірний, користувача зареєстровано.'}, status=status.HTTP_200_OK)
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

# Скидання пароля: форма для запиту на скидання
def reset_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = get_user_model().objects.get(email=email)
            reset_token = get_random_string(length=32)

            # Зберігаємо токен у профілі або окремій моделі
            user.profile.reset_token = reset_token  # Приклад
            user.profile.save()

            reset_link = f"{request.scheme}://{request.get_host()}/reset-password-confirm/{reset_token}/"
            send_mail(
                'Відновлення пароля',
                f'Для відновлення пароля натисніть: {reset_link}',
                settings.DEFAULT_FROM_EMAIL,
                [email]
            )
            return render(request, 'api/reset_password.html', {'message': 'Інструкція з відновлення пароля відправлена на вашу пошту.'})

        except get_user_model().DoesNotExist:
            return render(request, 'api/reset_password.html', {'error': 'Користувача з такою електронною поштою не знайдено.'})

    return render(request, 'api/reset_password.html')

# Налаштування логування
logger = logging.getLogger(__name__)

def generate_token(length=32):
    """
    Генерація випадкового токена.
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        user = get_user_model().objects.filter(email=email).first()
        if not user:
            return Response({'error': 'No user found with this email'}, status=status.HTTP_404_NOT_FOUND)

        reset_token = generate_token(32)
        cache_key = f"reset_token_{user.id}"
        cache.set(cache_key, reset_token, timeout=3600)

        reset_link = f"{request.scheme}://{request.get_host()}/reset-password/{reset_token}/"
        try:
            send_mail(
                'Password Reset Request',
                f'Your reset link: {reset_link}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )
            return Response({'message': 'Password reset email sent successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'Failed to send email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Підтвердження скидання пароля
class ResetPasswordConfirmView(APIView):
    def post(self, request, token):
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not new_password or not confirm_password:
            return Response({'error': 'Обидва поля пароля обов’язкові.'}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({'error': 'Паролі не співпадають.'}, status=status.HTTP_400_BAD_REQUEST)

        user_id = cache.get(f'reset_token_{token}')
        if not user_id:
            return Response({'error': 'Токен недійсний або прострочений.'}, status=status.HTTP_400_BAD_REQUEST)

        user = get_user_model().objects.filter(id=user_id).first()
        if not user:
            return Response({'error': 'Користувача не знайдено.'}, status=status.HTTP_404_NOT_FOUND)

        user.password = make_password(new_password)
        user.save()
        cache.delete(f'reset_token_{token}')

        return Response({'message': 'Пароль успішно змінено.'}, status=status.HTTP_200_OK)

def new_password_view(request, token):
    if request.method == 'GET':
        # Рендеримо форму введення нового пароля
        return render(request, 'api/new_password.html', {'token': token})

    elif request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not new_password or not confirm_password:
            return render(request, 'api/new_password.html', {
                'error': 'Всі поля є обов’язковими.',
                'token': token
            })

        if new_password != confirm_password:
            return render(request, 'api/new_password.html', {
                'error': 'Паролі не співпадають.',
                'token': token
            })

        # Перевірка токена
        user_id = cache.get(f'reset_token_{token}')
        if not user_id:
            return render(request, 'api/new_password.html', {
                'error': 'Токен недійсний або прострочений.',
                'token': token
            })

        # Змінюємо пароль користувача
        User = get_user_model()
        user = User.objects.filter(id=user_id).first()
        if not user:
            return render(request, 'api/new_password.html', {
                'error': 'Користувача не знайдено.',
                'token': token
            })

        user.password = make_password(new_password)
        user.save()
        cache.delete(f'reset_token_{token}')

        return render(request, 'api/new_password.html', {
            'success': 'Пароль успішно змінено. Тепер ви можете увійти.',
        })
