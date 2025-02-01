import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Ваші дані для входу
email_user = 'algowizzards.feedback@gmail.com'  # Ваш email
email_password = 'pxez grlq jfnk yuaw'  # Ваш пароль додатку
email_recipient = 'gamelag11123@gmail.com'  # Пошта отримувача для тестування

subject = "Тестовий лист"
body = "Це тестовий лист для перевірки відправки через Gmail SMTP сервер."

# Формуємо MIME повідомлення
message = MIMEMultipart()
message['From'] = email_user
message['To'] = email_recipient
message['Subject'] = subject
message.attach(MIMEText(body, 'plain', 'utf-8'))  # Вказуємо кодування UTF-8

try:
    # Підключення до SMTP сервера Gmail
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()  # Шифрування TLS
        server.login(email_user, email_password)  # Логін в Gmail
        print("Успішно підключено до сервера!")

        # Надсилання листа
        server.sendmail(email_user, email_recipient, message.as_string())
        print(f"Лист надіслано на {email_recipient}")

except smtplib.SMTPAuthenticationError:
    print("Помилка аутентифікації! Перевірте правильність вашого паролю додатку.")
except smtplib.SMTPException as e:
    print(f"Помилка при підключенні до сервера: {e}")
