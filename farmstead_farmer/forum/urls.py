from django.urls import path
from . import views

urlpatterns = [
    path('', views.forum_main, name='forum_main'),
    path('test', views.discussion_detail, name='test_discussion'),
    path('create-discussion', views.new_discussion, name = 'new_discussion')
]