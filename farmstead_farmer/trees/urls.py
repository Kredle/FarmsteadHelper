from django.urls import path
from . import views

urlpatterns = [
    path('', views.tree_list, name='tree_list'),  # Список тварин
    path('<int:id>/', views.sort_detail, name='tree_detail'),
]
