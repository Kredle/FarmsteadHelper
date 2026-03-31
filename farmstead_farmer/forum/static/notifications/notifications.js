async function updateNotifications() {
    const token = localStorage.getItem('authToken');
    if (!token) return;

    try {
        const response = await fetch('/forum/api/get_notifications/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ token: token })
        });

        if (!response.ok) return;

        const data = await response.json();
        const list = data.notifications || [];
        
        // Знаходимо всі обгортки сповіщень (і в хедері, і в сайдбарі)
        const wrappers = document.querySelectorAll('.notif-wrapper');

        wrappers.forEach(wrapper => {
            // Використовуємо селектор атрибутів, щоб обійти обмеження getElementById при дублікатах
            const badge = wrapper.querySelector('.notif-badge');
            const mailIcon = wrapper.querySelector('[id="mail-icon"]');
            const container = wrapper.querySelector('[id="notif-list"]');

            if (!badge || !mailIcon || !container) return;

            // Оновлюємо лічильник та іконку
            // Завжди показуємо звичайний конверт, але лише з числом якщо є сповіщення
            mailIcon.textContent = '✉️'; // Завжди звичайний конверт
            if (list.length > 0) {
                badge.style.display = 'block';
                badge.textContent = list.length > 999 ? '999+' : list.length;
            } else {
                badge.style.display = 'none';
            }

            // Рендеримо список
            if (list.length === 0) {
                container.innerHTML = '<div class="notif-item" style="text-align:center; color: #999;">Немає нових сповіщень</div>';
            } else {
                container.innerHTML = "";
                list.forEach(n => {
                    const div = document.createElement('div');
                    div.className = 'notif-item';
                    div.textContent = n.content;
                    div.title = n.content;
                    
                    // Переконайтеся, що n.id існує. Додамо лог для перевірки:
                    console.log("Rendering notif:", n); 

                    div.onclick = async (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    try {
                        const response = await fetch('/forum/api/mark_notification_read/', {
                            method: 'POST',
                            headers: { 
                                'Content-Type': 'application/json',
                                'X-CSRFToken': getCookie('csrftoken')
                            },
                            body: JSON.stringify({ 
                                token: token, 
                                notification_id: n.id 
                            })
                        });

                        if (response.ok) {
                            // МИТТЄВО видаляємо елемент з DOM для ефекту швидкодії
                            div.remove();
                            
                            // Отримуємо поточну кількість та зменшуємо її
                            const currentBadge = document.querySelector('.notif-badge');
                            if (currentBadge) {
                                const count = parseInt(currentBadge.textContent) - 1;
                                refreshBadgeCount(count >= 0 ? count : 0);
                            }

                            // Тільки після візуального оновлення переходимо
                            setTimeout(() => {
                                window.location.href = n.link;
                            }, 100); 
                        } else {
                            window.location.href = n.link;
                        }
                    } catch (err) {
                        window.location.href = n.link;
                    }
                };
                    container.appendChild(div);
                });
            }
        });
    } catch (e) {
        console.error('Помилка завантаження сповіщень:', e);
    }
}

function refreshBadgeCount(newCount) {
    const badges = document.querySelectorAll('.notif-badge');
    const mailIcons = document.querySelectorAll('[id="mail-icon"]');
    
    badges.forEach(badge => {
        if (newCount > 0) {
            badge.style.display = 'block';
            badge.textContent = newCount > 999 ? '999+' : newCount;
        } else {
            badge.style.display = 'none';
        }
    });

    // Завжди показуємо звичайний конверт
    mailIcons.forEach(icon => {
        icon.textContent = '✉️';
    });
}

// Керування випадаючим меню
function initNotificationEvents() {
    const wrappers = document.querySelectorAll('.notif-wrapper');

    wrappers.forEach(wrapper => {
        const icon = wrapper.querySelector('[id="notif-icon"]');
        const dropdown = wrapper.querySelector('[id="notif-dropdown"]');

        if (icon && dropdown) {
            icon.onclick = (e) => {
                e.stopPropagation();
                dropdown.classList.toggle('hidden');
            };
        }
    });

    // Закриваємо при кліку будь-де (вішаємо обробник тільки один раз)
    if (!window.notificationClickAttached) {
        document.addEventListener('click', (e) => {
            // Отримуємо актуальний список обгорток на момент кліку
            const currentWrappers = document.querySelectorAll('.notif-wrapper');
            currentWrappers.forEach(wrapper => {
                const icon = wrapper.querySelector('[id="notif-icon"]');
                const dropdown = wrapper.querySelector('[id="notif-dropdown"]');
                // Закриваємо тільки якщо клік не по іконці І не по самому меню
                if (icon && dropdown && !icon.contains(e.target) && !dropdown.contains(e.target)) {
                    dropdown.classList.add('hidden');
                }
            });
        });
        window.notificationClickAttached = true;
    }
}

// Запуск
document.addEventListener('DOMContentLoaded', () => {
    initNotificationEvents();
    updateNotifications();
    // Short polling: кожні 20 секунд
    setInterval(updateNotifications, 20000);
});

// Додаємо повторну ініціалізацію для випадків, коли innerHTML переписується
if (!window.notificationObserver) {
    window.notificationObserver = new MutationObserver(() => {
        initNotificationEvents();
    });
    window.notificationObserver.observe(document.body, { childList: true, subtree: true });
}