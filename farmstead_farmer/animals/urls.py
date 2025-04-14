from django.urls import path
from . import views

urlpatterns = [
    path('', views.animal_list, name='animal_list'),  # Список тварин
    path('<int:animal_id>/', views.animal_sorts, name='animal_detail'),
    path('<int:animal_id>/<int:sort_id>/', views.animal_detail, name='sort_detail'),
]
