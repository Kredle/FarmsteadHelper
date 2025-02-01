from django.urls import path
from . import views

urlpatterns = [
    path('catalog', views.catalog_view, name='catalog'),
    path('api/search/', views.search_api, name='search_api'),
]