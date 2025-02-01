document.getElementById('registration-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const password = document.getElementById('password').value;
    const repeatPassword = document.getElementById('repeat_password').value;
    const agreeTerms = document.getElementById('agree-terms').checked;
    const agreeData = document.getElementById('agree-data').checked;
    const email = document.getElementById('email').value;

    const errorMessage = document.getElementById('error-message');

    // Перевірка пароля
    if (password.length < 8) {
        errorMessage.textContent = 'Пароль має містити не менше 8 символів.';
        return;
    }

    if (password !== repeatPassword) {
        errorMessage.textContent = 'Паролі не співпадають. Будь ласка, перевірте.';
        return;
    }

    if (!agreeTerms || !agreeData) {
        errorMessage.textContent = 'Ви повинні погодитися з умовами використання та обробкою персональних даних.';
        return;
    }

    errorMessage.textContent = '';

    try {
        // Перевірка наявності email у базі
        const checkResponse = await fetch('/api/check-user/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email }),
        });

        const checkResult = await checkResponse.json();

        if (!checkResponse.ok) {
            errorMessage.textContent = checkResult.error || 'Цей логін або email вже використовується.';
            return; // Зупиняємо виконання, якщо email вже зайнятий
        }

        // Якщо email доступний, надсилаємо OTP
        const otpResponse = await fetch('/api/send-otp/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email }),
        });

        const otpResult = await otpResponse.json();

        if (!otpResponse.ok) {
            throw new Error(otpResult.error || `HTTP Error: ${otpResponse.status}`);
        }

        alert(otpResult.message || 'OTP успішно надіслано!');

        // Оновлений редірект на /confirm-register без префікса 'register/api/'
        window.location.href = '/confirm-register/';  // Перехід на правильний шлях
    } catch (err) {
        console.error('Помилка:', err);
        errorMessage.textContent = 'Не вдалося завершити реєстрацію. Спробуйте знову.';
    }
});