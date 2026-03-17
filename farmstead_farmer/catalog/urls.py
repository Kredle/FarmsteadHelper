from django.urls import path
from . import views

urlpatterns = [
    path('catalog', views.catalog_view, name='catalog'),
    path('api/search/', views.search_api, name='search_api'),
    path('api/filter_catalog/', views.filter_catalog_api, name='filter_catalog_api'),
    path('api/catalog-items/', views.catalog_items_api, name='catalog_items_api'),
    path('api/animals/', views.animals_list_api, name='animals_list_api'),
    path('api/animals/<int:animal_id>/', views.animal_sorts_api, name='animal_sorts_api'),
    path('api/animals/<int:animal_id>/<int:sort_id>/', views.animal_detail_api, name='animal_detail_api'),
]