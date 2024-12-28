from django.urls import path
from . import views

urlpatterns = [
    path('', views.tree_list, name='tree_list'),
    path('<int:tree_id>/<int:sort_id>/', views.sort_detail, name='sort_detail'),
    path('<int:tree_id>/', views.tree_sorts, name='tree_sorts'),
]
