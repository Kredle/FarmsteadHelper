from django.shortcuts import render
from django.core.mail import EmailMessage
from django.http import JsonResponse
from .forms import FeedbackForm
from django.conf import settings
import logging

# Налаштування логування
logger = logging.getLogger(__name__)

def feedback_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST, request.FILES)
        if form.is_valid():
            # Зібрати дані з форми
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            file = form.cleaned_data.get('file')

            try:
                email_message = EmailMessage(
                    subject=f"Новий фідбек від {name}",
                    body=f"Ім'я: {name}\nEmail: {email}\n\nПовідомлення:\n{message}",
                    from_email=settings.EMAIL_HOST_USER,
                    to=['gamelag11123@gmail.com', 'andriikravchuk.education@gmail.com'],
                )

                if file:
                    email_message.attach(file.name, file.read(), file.content_type)
                    logger.info(f"Файл прикріплено: {file.name}")

                email_message.send()
                logger.info("Email with attachment successfully sent.")
                return JsonResponse({"message": "Дякуємо за ваш фідбек!"})

            except Exception as e:
                logger.error(f"Error sending email with attachment: {e}")
                return JsonResponse({"message": "Щось пішло не так при надсиланні листа."}, status=500)
        else:
            return JsonResponse({"message": "Форма некоректна, будь ласка, перевірте введені дані."}, status=400)

    else:
        form = FeedbackForm()

    return render(request, 'feedback/feedback_form.html', {'form': form})
