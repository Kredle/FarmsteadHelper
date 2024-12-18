document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    const errorMessage = document.getElementById('error-message');

    // Перевірка на порожні поля
    if (!username || !password) {
        errorMessage.textContent = 'Будь ласка, заповніть усі поля.';
        return;
    }

    // Створення об'єкта даних для логіну
    const data = {
        username: username,
        password: password,
    };

    // Конвертуємо об'єкт у JSON з подвійними лапками для ключів
    const jsonData = JSON.stringify(data);

    // Перевірка даних перед відправкою
    console.log(jsonData);

    // Надсилання даних на сервер
    try {
        const response = await fetch('/api/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: jsonData,
        });

        const result = await response.json();  // Очікуємо відповідь у форматі JSON

        if (response.ok) {
            // Якщо все добре, зберігаємо токен в localStorage
            localStorage.setItem('authToken', result.token);
            // Перенаправлення на панель керування після успішного входу !!! тут поміняти на наступне
            window.location.href = '/dashboard';
        } else {
            // Якщо сервер повертає помилку, показуємо її
            errorMessage.textContent = result.detail || 'Невірний логін або пароль.';
        }
    } catch (err) {
        errorMessage.textContent = 'Помилка зв’язку з сервером.';
        console.error(err);
    }
});
