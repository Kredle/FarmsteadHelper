from django.urls import path
from .views import *

urlpatterns = [
    path('', map_overview, name='map_overview'),
    path('my-maps/', map_my_maps, name='map_my_maps'),
    path('subscription/', map_subscription, name='map_subscription'),
    path('interactive-map/', map_view, name='interactive-map'),
    path('save-interactive-map/', save_map, name='save-map'),
    path('check-map/', check_map, name='check-map'),
    path('profile-maps/', profile_maps, name='profile-maps'),
    path('list-maps/', list_maps, name='list-maps'),
    path('update-map-settings/', update_map_settings, name='update-map-settings'),
    path('delete-map/', delete_map, name='delete-map'),
    path('get-map/<int:user_id>/', get_map, name='get-map'),
    path('update-interactive-map/', update_map, name='update-map'),
    path('get_tree_sorts/', get_tree_sorts, name='get_tree_sorts'),
    path('get_vegetable_sorts/', get_vegetable_sorts, name='get_vegetable_sorts'),
    path('compatibility-index/', get_compatibility_index, name='map_compatibility_index'),
]