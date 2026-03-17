from django.shortcuts import render
from django.core.mail import EmailMessage
from django.http import JsonResponse
from .forms import FeedbackForm
from django.conf import settings
from farmstead_farmer import settings
from core.infrastructure.repositories import DjangoUserRepository
import requests
import logging
from api.throttles import SendOTPThrottle
from rest_framework.decorators import throttle_classes
logger = logging.getLogger(__name__)
_user_repo = DjangoUserRepository()

@throttle_classes([SendOTPThrottle])
def feedback_view(request):
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 Mb
    if request.method == 'POST':
        form = FeedbackForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            file = form.cleaned_data.get('file')
            recapcha_token = form.cleaned_data['recaptcha']
            print(recapcha_token)
            if file and file.size > MAX_FILE_SIZE:
                return JsonResponse({"message": "Розмір файлу перевищує ліміт 5 МБ."}, status=400)
            
            captcha_url = "https://www.google.com/recaptcha/api/siteverify"
            captcha_response = requests.post(captcha_url, data={'secret': settings.ReCapcha_secret_key, 'response': recapcha_token})
            captcha_result = captcha_response.json()

            if not captcha_result.get("success", False):
                return JsonResponse({"message": "Час дії капчі вичерпався."}, status=400)
            staff_emails = _user_repo.get_staff_emails()

            if not staff_emails:
                logger.warning("No staff users found to send the email.")
                return JsonResponse({"message": "Немає доступних отримувачів."}, status=400)

            try:
                email_message = EmailMessage(
                    subject=f"Новий фідбек від {name}",
                    body=f"Ім'я: {name}\nEmail: {email}\n\nПовідомлення:\n{message}",
                    from_email=settings.EMAIL_HOST_USER,
                    to=staff_emails,
                )

                if file:
                    email_message.attach(file.name, file.read(), file.content_type)
                    logger.info(f"Файл прикріплено: {file.name}")

                email_message.send()
                logger.info("Email successfully sent to staff users.")
                return JsonResponse({"message": "Дякуємо за ваш фідбек!"})

            except Exception as e:
                logger.error(f"Error sending email: {e}")
                return JsonResponse({"message": "Щось пішло не так при надсиланні листа."}, status=500)
        else:
            return JsonResponse({"message": "Форма некоректна, будь ласка, перевірте введені дані."}, status=400)

    else:
        form = FeedbackForm()

    return render(request, 'feedback/feedback_form.html', {'form': form})
