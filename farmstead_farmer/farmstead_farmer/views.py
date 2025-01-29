from django.shortcuts import render

def error_page(request, exception=None, error_code=500):
    error_messages = {
        400: "Помилка запиту. Синтаксична помилка або некоректні дані в запиті. Будь ласка, перевірте введену інформацію та спробуйте знову.",
        403: "Доступ заборонений. Ви не маєте прав для перегляду цієї сторінки.",
        404: "Сторінку не знайдено. Можливо, вона була видалена або ніколи не існувала.",
        500: "Сталася помилка на сервері. Спробуйте ще раз пізніше.",
    }
    
    message = error_messages.get(error_code, "Невідома помилка. Спробуйте пізніше.")
    
    return render(request, "error.html", {"error_code": error_code, "error_message": message})
