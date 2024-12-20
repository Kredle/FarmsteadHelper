from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .serializers import RegisterSerializer, LoginSerializer
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
import random
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
            send_mail(
                'Ваш OTP код',
                f'Ваш OTP код: {otp}',
                'from@example.com',
                [email],
                fail_silently=False,
            )
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
