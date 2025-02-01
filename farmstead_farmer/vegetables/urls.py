from django.urls import path
from . import views

urlpatterns = [
    path('', views.vegetable_list, name='vegetable_list'),
    path('<int:veg_id>/', views.vegetable_sorts, name='vegetable_sorts'),
    path('<int:veg_id>/<int:sort_id>/', views.sort_detail, name='sort_detail'),
]
