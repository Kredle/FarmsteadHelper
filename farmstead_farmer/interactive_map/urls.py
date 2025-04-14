from django.urls import path
from .views import *

urlpatterns = [
    path('', map_overview, name='map_overview'),
    path('interactive-map/', map_view, name='interactive-map'),
    path('save-interactive-map/', save_map, name='save-map'),
    path('check-map/', check_map, name='check-map'),
    path('get-map/<int:user_id>/', get_map, name='get-map'),
    path('update-interactive-map/', update_map, name='update-map'),
    path('get_tree_sorts/', get_tree_sorts, name='get_tree_sorts'),
    path('get_vegetable_sorts/', get_vegetable_sorts, name='get_vegetable_sorts')
]