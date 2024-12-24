from django.urls import path, include
from feedback.views import feedback_view

urlpatterns = [
    path('', include('api.urls')),
    path('feedback/', feedback_view, name='feedback'),
    path('catalog/animals/', include('animals.urls')),
    path('catalog/trees/', include('trees.urls')),
    path('', include('main_page.urls')),
]