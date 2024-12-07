const form = document.getElementById('registration-form');
const errorMessage = document.getElementById('error-message');
const responseMessage = document.getElementById('response-message');

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const password = document.getElementById('password').value;
    const repeatPassword = document.getElementById('repeat-password').value;
    const agreeTerms = document.getElementById('agree-terms').checked;
    const agreeData = document.getElementById('agree-data').checked;

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
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    // Надсилання даних на сервер
    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });

        const result = await response.json();
        if (response.ok) {
            responseMessage.textContent = 'Перевірте вашу пошту для підтвердження.';
        } else {
            responseMessage.textContent = result.error || 'Сталася помилка.';
        }
    } catch (err) {
        responseMessage.textContent = 'Помилка зв’язку з сервером.';
        console.error(err);
    }
});
