from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin

class CustomErrorMiddleware(MiddlewareMixin):
    """Middleware для обробки сторінок 400, 403, 404, 500 при DEBUG=True."""

    def process_response(self, request, response):
        error_templates = {
            400: "errors/400.html",
            403: "errors/403.html",
            404: "errors/404.html",
            500: "errors/500.html",
        }

        if response.status_code in error_templates:
            return render(request, error_templates[response.status_code], status=response.status_code)

        return response
