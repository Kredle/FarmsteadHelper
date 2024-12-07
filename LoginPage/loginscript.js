const form = document.getElementById('login-form');
const errorMessage = document.getElementById('error-message');

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Збір даних з форми
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    // Надсилання даних на сервер
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });

        const result = await response.json();
        if (response.ok) {
            window.location.href = '/dashboard'; // Перенаправлення на сторінку користувача
        } else {
            errorMessage.textContent = result.error || 'Невірний email або пароль.';
        }
    } catch (err) {
        errorMessage.textContent = 'Помилка зв’язку з сервером.';
        console.error(err);
    }
});
