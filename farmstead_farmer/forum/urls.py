from django.urls import path
from . import views
from api.views import login_view
urlpatterns = [
    path('', views.forum_main, name='forum_main'),
    path('test', views.discussion_detail, name='discussion_detail'),
    path('create-discussion/', views.new_discussion, name = 'new_discussion'),
    path('create/', views.create_discussion, name='create_discussion'),
    path('topic/<int:pk>/', views.topic_detail, name='topic_detail'), 
    path('get_topics', views.get_topics, name = 'get_topics'),
    path('get_popular_topics', views.get_popular_topics, name = 'get_popular_topics'),
    path('update_topic/<int:topic_id>/', views.update_topic_reaction, name='update_topic_reaction'),
    path('delete_topic/<int:topic_id>/', views.delete_topic, name='delete_topic'),
    path('edit-topic/<int:topic_id>/', views.edit_topic_new, name='edit_topic_new'),
    path('edit_topic/<int:topic_id>/', views.edit_topic, name='edit_topic'),
    path('add_comment/<int:topic_id>/', views.add_comment, name='add_comment'),
    path('get_user_reaction/<int:topic_id>/', views.get_user_reaction, name='get_user_reaction'),
    #path('increace_comment_counter_topic/<int:topic_id>/', views.increace_comment_counter_topic, name='increace_comment_counter_topic'),
    path('topic/<int:topic_id>/comments_list/', views.comments_list, name='comments_list'),
    path('update_comment/<int:comment_id>/', views.update_comment, name='update_comment'),
    path('delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('update-comment-reaction/', views.update_comment_reaction, name='update_comment_reaction'),
    path('edit_comment/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    #path('increace_comment_counter_comment/<int:parentCommentId>/', views.increace_comment_counter_comment, name='increace_comment_counter_comment'),
    path('get_comment/<int:comment_id>/', views.get_comment, name = 'get_comment'),
]
