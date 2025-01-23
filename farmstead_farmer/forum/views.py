from django.shortcuts import render, redirect, get_object_or_404
from .models import Topic, Comment
from .forms import DiscussionForm
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from api.models import CustomUser
def forum_main(request):
    topics = Topic.objects.all().values(
        'idTopic', 'Title', 'Content', 'Category', 'Author', 'Date', 'Likes', 'Comments'
    )
    return render(request, 'forumpage.html', {'topics': topics})

def get_topics(request):
    topics = Topic.objects.all()  # Отримуємо всі теми з бази даних
    topics_list = list(topics.values())  # Перетворюємо QuerySet в список словників
    return JsonResponse(topics_list, safe=False)

def discussion_detail(request):
    return render(request, 'discussion_detail.html')

def new_discussion(request):
    return render(request, 'create_discussion.html')

def create_discussion(request):
    if request.method == 'POST':
        category = request.POST.get('category_text')
        title = request.POST.get('title')
        description = request.POST.get('description')
        author = request.POST.get('username')
        time = request.POST.get('created_time')
        date = request.POST.get('created_date')
        likes = request.POST.get('likes')
        dislikes = request.POST.get('dislikes')
        comments = request.POST.get('comm')
        topic = Topic.objects.create(Category=category, Title=title, Content=description, Author = author, Time = time, Date = date, Likes = likes, Dislikes = dislikes, Comments = comments, Likes_list = '[]', Dislikes_list = '[]' )
        topic_id = topic.idTopic
        print(topic_id)
        return redirect('topic_detail', topic_id)  # Перенаправлення на список обговорень
    print(request.method)
    return render(request, 'create_discussion.html')

def topic_detail(request, pk):
    # Отримуємо тему за її первинним ключем
    topic = get_object_or_404(Topic, pk=pk)
    return render(request, 'topic_detail.html', {'topic': topic})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def update_topic_reaction(request, topic_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            token = data.get('token')
            status = data.get('status')

            if not token or not status:
                return JsonResponse({'error': 'Token and status are required'}, status=400)

            try:
                user = CustomUser.objects.get(auth_token=token)
            except CustomUser.DoesNotExist:
                return JsonResponse({'error': 'Invalid token'}, status=401)

            topic = Topic.objects.get(idTopic=topic_id)
            username = user.username

            # Reset status
            if status == "reset":
                if username in topic.Likes_list:
                    topic.Likes_list.remove(username)
                    topic.Likes -= 1
                if username in topic.Dislikes_list:
                    topic.Dislikes_list.remove(username)
                    topic.Dislikes -= 1

            # Like status
            elif status == "like":
                if username not in topic.Likes_list:
                    topic.Likes_list.append(username)
                    topic.Likes += 1
                if username in topic.Dislikes_list:
                    topic.Dislikes_list.remove(username)
                    topic.Dislikes -= 1

            # Dislike status
            elif status == "dislike":
                if username not in topic.Dislikes_list:
                    topic.Dislikes_list.append(username)
                    topic.Dislikes += 1
                if username in topic.Likes_list:
                    topic.Likes_list.remove(username)
                    topic.Likes -= 1

            topic.save()

            return JsonResponse({
                'Likes': topic.Likes,
                'Dislikes': topic.Dislikes,
                'Likes_list': topic.Likes_list,
                'Dislikes_list': topic.Dislikes_list
            }, status=200)

        except Topic.DoesNotExist:
            return JsonResponse({'error': 'Topic not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def get_user_reaction(request, topic_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            token = data.get('token')

            if not token:
                return JsonResponse({'error': 'Token is required'}, status=400)

            try:
                user = CustomUser.objects.get(auth_token=token)
            except CustomUser.DoesNotExist:
                return JsonResponse({'error': 'Invalid token'}, status=401)

            topic = Topic.objects.get(idTopic=topic_id)
            username = user.username

            if username in topic.Likes_list:
                return JsonResponse({'status': 'like'}, status=200)
            elif username in topic.Dislikes_list:
                return JsonResponse({'status': 'dislike'}, status=200)
            else:
                return JsonResponse({'status': 'reset'}, status=200)

        except Topic.DoesNotExist:
            return JsonResponse({'error': 'Topic not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def delete_topic(request, topic_id):
    # Перевіряємо, чи це POST запит
    if request.method == 'POST':
        data = json.loads(request.body)
        user = data.get('username')
        topic = get_object_or_404(Topic, idTopic=topic_id)
        
        if topic.Author == user:  # Перевіряємо, чи це автор теми
            topic.delete()  # Видаляємо тему
            return redirect('forum_main')  # Перенаправляємо на список тем
        else:
            return redirect('forum_main')  # Якщо не автор, перенаправляємо на головну

def edit_topic_new(request, topic_id):
    context = {
        'topic_id': topic_id  # Передаємо topic_id у контекст
    }
    return render(request, 'edit_topic.html', context)

def edit_topic(request, topic_id):
    if request.method == 'POST':
        user = request.POST.get('username')
        topic = get_object_or_404(Topic, idTopic=topic_id)
        if topic.Author == user:  # Перевіряємо, чи це автор теми
            topic.Category= request.POST.get('category_text')
            topic.Content = request.POST.get('description')
            topic.Title = request.POST.get('title')
            topic.Time = request.POST.get('created_time')
            topic.Date = request.POST.get('created_date')
            topic.save()
            #topic_id = topic.idTopic
            return redirect('topic_detail', topic_id)
        else:
            return redirect('forum_main')  # Якщо не автор, перенаправляємо на головну

@csrf_exempt
def add_comment(request, topic_id):
    print(request.method)
    print(request.body)
    print(request.headers)
    #topic = get_object_or_404(Topic, idTopic=topic_id)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f"Дані коментаря: {data}")

            comment = Comment(
                Content=data.get('Content'),
                Likes=0,
                Dislikes=0,
                Comments=0,
                Date=data.get('Date'),
                Time=data.get('Time'),
                Author=data.get('Author'),
                Topics_id=data.get('Topics_id'),
                Receiver=data.get('Receiver'),
                IsAnswer=data.get('IsAnswer'),
            )
            comment.save()
            return JsonResponse({'message': 'Коментар успішно додано!'}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Невірний формат JSON'}, status=400)
        except Exception as e:
            print(f"Помилка при додаванні коментаря: {e}")
            return JsonResponse({'error': 'Не вдалося додати коментар.'}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def increace_comment_counter_topic(request, topic_id):
    print(f"Метод запиту: {request.method}")
    print(f"Шлях запиту: {request.path}")
    topic = Topic.objects.get(idTopic=topic_id)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            comments_counter = data.get('Comments')
            if comments_counter is None:
                return JsonResponse({'error': 'Поле Comments відсутнє в запиті'}, status=400)
            topic.Comments = int(comments_counter) + 1
            topic.save()
            return JsonResponse(status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Невірний формат JSON'}, status=400)
        except Exception as e:
            print(f"Помилка при збільшенні лічильника коментарів: {e}")
            return JsonResponse({'error': 'Не вдалося збільшети лічильник коментарів.'}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)
    
def get_popular_topics(request):
    # Отримуємо теми з бази даних, сортуємо їх за лайками у порядку спадання
    topics = Topic.objects.all().order_by('-Likes')  # Поле `likes` повинно бути у вашій моделі
    popular_topics_list = list(topics.values())  # Перетворюємо QuerySet в список словників
    return JsonResponse(popular_topics_list, safe=False)

def comments_list(request, topic_id):
    comments = Comment.objects.filter(Topics_id=topic_id).values('Author', 'Content', 'Likes', 'Dislikes', 'Comments', 'Date', 'Time')
    return JsonResponse(list(comments), safe=False)
