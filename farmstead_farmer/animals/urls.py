from django.urls import path
from . import views

urlpatterns = [
    path('', views.animal_list, name='animal_list'),  # Список тварин
    path('<int:id>/', views.animal_detail, name='animal_detail'),  # Деталі конкретної тварини
]
