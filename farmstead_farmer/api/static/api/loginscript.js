document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorMessage = document.getElementById('error-message');

    // Отримуємо відповідь reCAPTCHA
    const recaptchaResponse = grecaptcha.getResponse();

    // Перевірка на порожні поля
    if (!username || !password) {
        errorMessage.textContent = 'Будь ласка, заповніть усі поля.';
        return;
    }

    // Перевірка reCAPTCHA
    if (!recaptchaResponse) {
        errorMessage.textContent = 'Будь ласка, пройдіть reCAPTCHA';
        return;
    }

    // Створення об'єкта даних для логіну
    const data = {
        username: username,
        password: password,
        recaptcha_token: recaptchaResponse // Додаємо токен reCAPTCHA
    };

    // Надсилання даних на сервер
    try {
        const response = await fetch('/api/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        const result = await response.json();

        if (response.ok) {
            localStorage.setItem('authToken', result.token);
            window.location.href = '/';
        } else {
            errorMessage.textContent = result.detail || 'Невірний логін або пароль.';
            grecaptcha.reset(); 
        }
    } catch (err) {
        errorMessage.textContent = 'Помилка зв’язку з сервером.';
        grecaptcha.reset();
        console.error(err);
    }
});