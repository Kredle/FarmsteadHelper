from django.urls import path
from . import views

urlpatterns = [
    path('catalog', views.catalog_view, name='catalog'),
    path('api/search/', views.search_api, name='search_api'),
    path('api/filter_catalog/', views.filter_catalog_api, name='filter_catalog_api')
]