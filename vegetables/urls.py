from django.urls import path
from . import views

urlpatterns = [
    path('', views.vegetable_list, name='vegetable_list'),
    path('<int:id>/', views.sort_detail, name='vegetable_detail'),
]
