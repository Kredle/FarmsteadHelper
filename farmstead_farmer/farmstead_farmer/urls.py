from django.urls import path, include
from feedback.views import feedback_view
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.views.generic import TemplateView

from django.urls import path
from .views import trigger_400, trigger_403, trigger_404, trigger_500

urlpatterns = [
    path('feedback/', feedback_view, name='feedback'),
    path('catalog/animals/', include('animals.urls')),
    path('catalog/trees/', include('trees.urls')),
    path('catalog/vegetables/', include('vegetables.urls')),
    path('catalog/flowers/', include('plants.urls')),
    path('forum/', include('forum.urls')),
    path('map/', include('interactive_map.urls')),
    path('', include('main_page.urls')),  # Загальний шлях для головної сторінки
    path('', include('api.urls')),       # Загальний шлях для API
    path('', include('catalog.urls')),   # Загальний шлях для каталогу
    path("400/", trigger_400),
    path("403/", trigger_403),
    path("404/", trigger_404),
    path("500/", trigger_500),
]


