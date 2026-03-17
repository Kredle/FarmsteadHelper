import json

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

from rest_framework.decorators import throttle_classes, api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import UserRateThrottle

from core.application.forum import ForumUseCase
from core.application.favorites import FavoriteUseCase
from core.domain.exceptions import InvalidTokenError, MissingFieldError
from core.infrastructure.forum_repositories import DjangoForumRepository, TopicNotFoundError, CommentNotFoundError
from core.infrastructure.repositories import DjangoUserRepository


class ForumTrottling(UserRateThrottle):
    rate = '100/minute'


_user_repo = DjangoUserRepository()
_forum_repo = DjangoForumRepository()
forum_use_case = ForumUseCase(_forum_repo, _user_repo)
favorite_use_case = FavoriteUseCase(_user_repo)


def forum_main(request):
    return render(request, 'forumpage.html')


@throttle_classes([ForumTrottling])
def get_topics(request):
    topics = forum_use_case.get_topics()
    return JsonResponse(topics, safe=False)


def discussion_detail(request):
    return render(request, 'discussion_detail.html')


def new_discussion(request):
    return render(request, 'create_discussion.html')


@throttle_classes([ForumTrottling])
def create_discussion(request):
    if request.method == 'POST':
        topic_id = forum_use_case.create_topic(
            category=request.POST.get('category_text'),
            title=request.POST.get('title'),
            content=request.POST.get('description'),
            author=request.POST.get('username'),
            time=request.POST.get('created_time'),
            date=request.POST.get('created_date'),
            likes=request.POST.get('likes'),
            dislikes=request.POST.get('dislikes'),
            comments=request.POST.get('comm'),
        )
        return redirect('topic_detail', topic_id)
    return render(request, 'create_discussion.html')


def topic_detail(request, pk):
    topic_data = forum_use_case.topic_detail(pk)
    if topic_data is None:
        return redirect('forum_main')
    topic = {
        'idTopic': topic_data.get('id'),
        'Title': topic_data.get('title'),
        'Content': topic_data.get('content'),
        'Category': topic_data.get('category'),
        'Author': topic_data.get('author'),
        'Date': topic_data.get('date'),
        'Time': topic_data.get('time'),
        'Likes': topic_data.get('likes'),
        'Dislikes': topic_data.get('dislikes'),
        'Comments': topic_data.get('comments'),
        'Likes_list': topic_data.get('likes_list'),
        'Dislikes_list': topic_data.get('dislikes_list'),
    }
    return render(request, 'topic_detail.html', {'topic': topic})


@throttle_classes([ForumTrottling])
@csrf_exempt
def update_topic_reaction(request, topic_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            token = data.get('token')
            reaction = data.get('status')
            if not token or not reaction:
                return JsonResponse({'error': 'Token and status are required'}, status=400)
            result = forum_use_case.toggle_topic_reaction(topic_id, token, reaction)
            return JsonResponse(result, status=200)
        except TopicNotFoundError:
            return JsonResponse({'error': 'Topic not found'}, status=404)
        except InvalidTokenError:
            return JsonResponse({'error': 'Invalid token'}, status=401)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@throttle_classes([ForumTrottling])
@csrf_exempt
def update_comment_reaction(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            comment_id = data.get('id')
            token = data.get('token')
            reaction = data.get('status')
            if not token or not reaction or not comment_id:
                return JsonResponse({'error': 'Token, status and id are required'}, status=400)
            result = forum_use_case.toggle_comment_reaction(comment_id, token, reaction)
            return JsonResponse(result, status=200)
        except CommentNotFoundError:
            return JsonResponse({'error': 'Comment not found'}, status=404)
        except InvalidTokenError:
            return JsonResponse({'error': 'Invalid token'}, status=401)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


def get_comment(request, comment_id):
    if request.method == 'POST':
        data = forum_use_case.get_comment(comment_id)
        if data is None:
            return JsonResponse({'error': 'Comment not found'}, status=404)
        return JsonResponse({'status': 'success', **data}, status=201)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@throttle_classes([ForumTrottling])
@csrf_exempt
def get_user_reaction(request, topic_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            token = data.get('token')
            if not token:
                return JsonResponse({'error': 'Token is required'}, status=400)
            reaction = forum_use_case.get_user_topic_reaction(topic_id, token)
            return JsonResponse({'status': reaction}, status=200)
        except TopicNotFoundError:
            return JsonResponse({'error': 'Topic not found'}, status=404)
        except InvalidTokenError:
            return JsonResponse({'error': 'Invalid token'}, status=401)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@api_view(['POST'])
@throttle_classes([ForumTrottling])
def toggle_favorite_forum(request):
    try:
        payload = favorite_use_case.toggle(request.data.get('token'), request.data)
        return Response(payload, status=status.HTTP_200_OK)
    except MissingFieldError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except InvalidTokenError as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)


@api_view(['POST'])
@throttle_classes([ForumTrottling])
def check_favorite_forum(request):
    try:
        payload = favorite_use_case.check(request.data.get('token'), request.data)
        return Response(payload, status=status.HTTP_200_OK)
    except MissingFieldError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except InvalidTokenError as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)


@throttle_classes([ForumTrottling])
def delete_topic(request, topic_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        requesting_user = data.get('username')
        topic = forum_use_case.topic_detail(topic_id)
        if topic is None:
            return redirect('forum_main')

        if topic['author'] == requesting_user:
            topic_url = request.build_absolute_uri(
                reverse('topic_detail', args=[topic_id])
            )
            forum_use_case.delete_topic(topic_id, topic_url)
        return redirect('forum_main')
    return redirect('forum_main')


def edit_topic_new(request, topic_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            forum_use_case.update_topic(
                topic_id,
                title=data.get('title'),
                content=data.get('content'),
                category=data.get('category'),
            )
            return JsonResponse({'status': 'success', 'redirect_url': f'/topic/{topic_id}'})
        except TopicNotFoundError:
            return JsonResponse({'error': 'Topic not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    topic = forum_use_case.topic_detail(topic_id)
    if topic is None:
        return redirect('forum_main')
    return render(request, 'edit_topic.html', {
        'topic_id': topic_id,
        'title': topic.get('title', ''),
        'content': topic.get('content', ''),
        'category': topic.get('category', ''),
    })


@throttle_classes([ForumTrottling])
def edit_topic(request, topic_id):
    if request.method == 'POST':
        user = request.POST.get('username')
        topic = forum_use_case.topic_detail(topic_id)
        if topic and topic['author'] == user:
            forum_use_case.update_topic(
                topic_id,
                title=request.POST.get('title'),
                content=request.POST.get('description'),
                category=request.POST.get('category_text'),
            )
            return redirect('topic_detail', topic_id)
        return redirect('forum_main')
    topic = forum_use_case.topic_detail(topic_id)
    if topic is None:
        return redirect('forum_main')
    return render(request, 'edit_topic.html', {
        'topic_id': topic_id,
        'title': topic.get('title', ''),
        'content': topic.get('content', ''),
        'category': topic.get('category', ''),
    })


@throttle_classes([ForumTrottling])
@csrf_exempt
def add_comment(request, topic_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            result = forum_use_case.create_comment(
                topic_id=topic_id,
                content=data.get('Content'),
                author=data.get('Author'),
                date=data.get('Date'),
                time=data.get('Time'),
                topics_id=data.get('Topics_id'),
                receiver=data.get('Receiver'),
                is_answer=data.get('IsAnswer'),
                parent_id=data.get('ParentId'),
            )
            return JsonResponse(result, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def get_popular_topics(request):
    topics = forum_use_case.get_popular_topics()
    return JsonResponse(topics, safe=False)


def topic_detail_api(request, pk):
    data = forum_use_case.topic_detail(pk)
    if data is None:
        return JsonResponse({'error': 'Topic not found'}, status=404)
    return JsonResponse(data)


def comments_list(request, topic_id):
    comments = forum_use_case.get_comments_for_topic(topic_id)
    return JsonResponse(comments, safe=False)


@throttle_classes([ForumTrottling])
@csrf_exempt
def update_comment(request, comment_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            content = data.get('Content')
            if not content:
                return JsonResponse({'error': 'Content cannot be empty'}, status=400)
            forum_use_case.update_comment(comment_id, content)
            return JsonResponse({'message': 'Comment updated'}, status=200)
        except CommentNotFoundError:
            return JsonResponse({'error': 'Comment not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@throttle_classes([ForumTrottling])
@csrf_exempt
def edit_comment(request, comment_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            content = data.get('Content')
            actor = data.get('User')
            if not content:
                return JsonResponse({'error': 'Content cannot be empty'}, status=400)
            forum_use_case.update_comment(comment_id, content, actor=actor)
            return JsonResponse({'message': 'Comment updated'}, status=200)
        except CommentNotFoundError:
            return JsonResponse({'error': 'Comment not found'}, status=404)
        except PermissionError:
            return JsonResponse({'message': 'Not the comment author'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@throttle_classes([ForumTrottling])
def delete_comment(request, comment_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        topic_id = data.get('topicId')
        forum_use_case.delete_comment(comment_id, topic_id)
        return redirect('forum_main')
    return JsonResponse({'error': 'Method not allowed'}, status=405)
