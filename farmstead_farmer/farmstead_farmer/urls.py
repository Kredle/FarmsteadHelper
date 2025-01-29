from django.urls import path, include
from feedback.views import feedback_view
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.views.generic import TemplateView


urlpatterns = [
    path('', include('api.urls')),
    path('feedback/', feedback_view, name='feedback'),
    path('catalog/animals/', include('animals.urls')),
    path('catalog/trees/', include('trees.urls')),
    path('', include('main_page.urls')),
    path('catalog/vegetables/', include('vegetables.urls')),
    path('catalog/flowers/', include('plants.urls')),
    path('', include('catalog.urls')),
    path('forum/', include('forum.urls')),
    path('map/', include('interactive_map.urls')),
]

from django.conf.urls import handler400, handler403, handler404, handler500
from .views import error_page

handler400 = lambda request, exception: error_page(request, exception, 400)
handler403 = lambda request, exception: error_page(request, exception, 403)
handler404 = lambda request, exception: error_page(request, exception, 404)
handler500 = lambda request: error_page(request, None, 500)
