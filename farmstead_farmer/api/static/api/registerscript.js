document.getElementById('registration-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const password = document.getElementById('password').value;
    const repeatPassword = document.getElementById('repeat_password').value;
    const agreeTerms = document.getElementById('agree-terms').checked;
    const agreeData = document.getElementById('agree-data').checked;

    const errorMessage = document.getElementById('error-message');
    const responseMessage = document.getElementById('response-message');

    // Перевірка довжини пароля
    if (password.length < 8) {
        errorMessage.textContent = 'Пароль має містити не менше 8 символів.';
        return;
    }

    // Перевірка на співпадіння паролів
    if (password !== repeatPassword) {
        errorMessage.textContent = 'Паролі не співпадають. Будь ласка, перевірте.';
        return;
    }

    // Перевірка згод
    if (!agreeTerms || !agreeData) {
        errorMessage.textContent = 'Ви повинні погодитися з умовами використання та обробкою персональних даних.';
        return;
    }

    // Очищення повідомлення про помилку
    errorMessage.textContent = '';

    // Збір даних з форми
    const formData = new FormData(document.getElementById('registration-form'));
    const data = {};

    formData.forEach((value, key) => {
        data[key] = value;
    });

    // Конвертуємо об'єкт у JSON з подвійними лапками для ключів
    const jsonData = JSON.stringify(data);

    // Перевірка даних перед відправкою
    console.log(jsonData);

    // Надсилання даних на сервер
    try {
        const response = await fetch('/api/register/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: jsonData,
        });

        const result = await response.json();
        if (response.ok) {
            responseMessage.textContent = '';
            setTimeout(() => {
                window.location.href = '/login/'; 
            }, 3000);
            document.getElementById('registration-form').reset(); // Очистити форму після успішної реєстрації
        } else {
            errorMessage.textContent = result.error || 'Цей логін або email вже використовується';
        }
    } catch (err) {
        errorMessage.textContent = 'Помилка зв’язку з сервером.';
        console.error(err);
    }
});
