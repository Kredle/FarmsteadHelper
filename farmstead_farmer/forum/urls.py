from django.urls import path
from . import views

urlpatterns = [
    path('', views.forum_main, name='forum_main'),
    path('test', views.discussion_detail, name='discussion_detail'),
    path('create-discussion/', views.new_discussion, name = 'new_discussion'),
    path('create/', views.create_discussion, name='create_discussion'),
    path('topic/<int:pk>/', views.topic_detail, name='topic_detail'), 
    path('get_topics', views.get_topics, name = 'get_topics'),
    path('update_topic/<int:topic_id>/', views.update_topic_reaction, name='update_topic_reaction'),
    path('delete_topic/<int:topic_id>/', views.delete_topic, name='delete_topic'),
    path('edit-topic/<int:topic_id>/', views.edit_topic_new, name='edit_topic_new'),
    path('edit_topic/<int:topic_id>/', views.edit_topic, name='edit_topic'),
    path('add_comment/<int:topic_id>/', views.add_comment, name='add_comment'),
]