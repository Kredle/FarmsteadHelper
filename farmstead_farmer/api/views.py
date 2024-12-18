from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .serializers import RegisterSerializer, LoginSerializer
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth.models import User


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
