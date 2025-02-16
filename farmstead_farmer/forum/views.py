from django.shortcuts import render, redirect, get_object_or_404
from .models import Topic, Comment
from .forms import DiscussionForm
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse,  HttpResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from api.models import CustomUser
from django.contrib import messages
from django.urls import reverse
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
    #print(f"Метод запиту: {request.method}")
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
            id = user.id
            #print(f"topic_id: {topic_id}")
            #print(f"token: {token}")
            #print(f"status: {status}")
            #print(f"id: {id}")
            #print(f"Likes_list: {topic.Likes_list}")
            if not isinstance(topic.Likes_list, list):
                try:
                    topic.Likes_list = json.loads(topic.Likes_list)  # Якщо поле зберігається як текст
                except (json.JSONDecodeError, TypeError):
                    topic.Likes_list = []
            if not isinstance(topic.Dislikes_list, list):
                try:
                    topic.Dislikes_list = json.loads(topic.Likes_list)  # Якщо поле зберігається як текст
                except (json.JSONDecodeError, TypeError):
                    topic.Dislikes_list = []
            # Reset status
            if status == "reset":
                if id in topic.Likes_list:
                    topic.Likes_list.remove(id)
                    topic.Likes -= 1
                if id in topic.Dislikes_list:
                    topic.Dislikes_list.remove(id)
                    topic.Dislikes -= 1

            # Like status
            elif status == "like":
                #print(f"Likes_list: {topic.Likes_list}")
                if id not in topic.Likes_list:
                    topic.Likes_list.append(id)
                    topic.Likes += 1
                    #print(f"Likes_list: {topic.Likes_list}")
                if id in topic.Dislikes_list:
                    topic.Dislikes_list.remove(id)
                    topic.Dislikes -= 1
                #print(f"Likes_list: {topic.Likes_list}")
            # Dislike status
            elif status == "dislike":
                if id not in topic.Dislikes_list:
                    topic.Dislikes_list.append(id)
                    topic.Dislikes += 1
                if id in topic.Likes_list:
                    topic.Likes_list.remove(id)
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
def update_comment_reaction(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            id = data.get('id')
            token = data.get('token')
            status = data.get('status')

            if not token or not status or not id:
                return JsonResponse({'error': 'Token and status and id are required'}, status=400)

            try:
                user = CustomUser.objects.get(auth_token=token)
            except CustomUser.DoesNotExist:
                return JsonResponse({'error': 'Invalid token'}, status=401)

            comment = Comment.objects.get(idComments=id)
            id_user = user.id

            # Reset status
            if status == "reset":
                if id_user in comment.Likes_list:
                    comment.Likes_list.remove(id_user)
                    comment.Likes -= 1
                if id_user in comment.Dislikes_list:
                    comment.Dislikes_list.remove(id_user)
                    comment.Dislikes -= 1

            # Like status
            elif status == "like":
                is_inside = True
                if id_user not in comment.Likes_list:
                    comment.Likes_list.append(id_user)
                    comment.Likes += 1
                    is_inside = False
                if id_user in comment.Dislikes_list:
                    comment.Dislikes_list.remove(id_user)
                    comment.Dislikes -= 1
                if is_inside:
                    comment.Likes_list.remove(id_user)
                    comment.Likes -= 1

            # Dislike status
            elif status == "dislike":
                is_inside = True
                if id_user not in comment.Dislikes_list:
                    comment.Dislikes_list.append(id_user)
                    comment.Dislikes += 1
                    is_inside = False
                if id_user in comment.Likes_list:
                    comment.Likes_list.remove(id_user)
                    comment.Likes -= 1
                if is_inside:
                    comment.Dislikes_list.remove(id_user)
                    comment.Dislikes -= 1

            comment.save()

            return JsonResponse({
                'Likes': comment.Likes,
                'Dislikes': comment.Dislikes,
                'Likes_list': comment.Likes_list,
                'Dislikes_list': comment.Dislikes_list
            }, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def get_comment(request, comment_id):
    #print(f"Метод запиту: {request.method}")
    if request.method == 'POST':
        comment = Comment.objects.get(idComments = comment_id)
        return JsonResponse({
                'status': 'success',
                'id': comment_id,
                'Author': comment.Author,
                'Content': comment.Content,
                'Date': comment.Date,
                'Time': comment.Time,
                'ParentId': comment.ParentId ,
                'Comments': 0
            }, status=201)
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
            id = user.id

            if id in topic.Likes_list:
                return JsonResponse({'status': 'like'}, status=200)
            elif id in topic.Dislikes_list:
                return JsonResponse({'status': 'dislike'}, status=200)
            else:
                return JsonResponse({'status': 'reset'}, status=200)

        except Topic.DoesNotExist:
            return JsonResponse({'error': 'Topic not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def delete_topic(request, topic_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        requesting_user = data.get('username')  # Змінна перейменована, щоб уникнути конфлікту імен
        topic = get_object_or_404(Topic, idTopic=topic_id)
        
        if topic.Author == requesting_user:
            # Видаляємо всі коментарі теми
            Comment.objects.filter(Topics_id=topic_id).delete()
            
            # Генеруємо повну URL-адресу теми
            topic_path = reverse('topic_detail', args=[topic_id])
            topic_url = request.build_absolute_uri(topic_path)
            print(f"{topic_url}")
            # Оновлюємо обране для всіх користувачів
            all_users = CustomUser.objects.all()
            for user in all_users:
                original_count = len(user.favorites)
                # Видаляємо всі входження цієї теми
                user.favorites = [fav for fav in user.favorites if fav.get('link') != topic_url]
                if len(user.favorites) != original_count:
                    user.save()  # Зберігаємо тільки при змінах
            
            # Видаляємо саму тему
            topic.delete()
            return redirect('forum_main')
        
        return redirect('forum_main')
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
    #print(request.method)
    #print(request.body)
    #print(request.headers)
    #topic = get_object_or_404(Topic, idTopic=topic_id)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            topic = Topic.objects.get(idTopic = topic_id)
            parent_comment_id = data.get('ParentId', None)
            parent_comment = None

            if parent_comment_id:
                parent_comment = Comment.objects.get(idComments=parent_comment_id)

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
                ParentId = data.get('ParentId')
            )
            topic.Comments += 1
            topic.save()

            # Оновлення лічильника коментарів у батьківського коментаря (якщо є)
            if parent_comment:
                parent_comment.Comments += 1
                parent_comment.save()

            comment.save()
            return JsonResponse({
                'status': 'success',
                'id': comment.idComments,
                'Author': comment.Author,
                'Content': comment.Content,
                'Date': comment.Date,
                'Time': comment.Time,
                'ParentId': parent_comment_id,
                'Comments': 0
            }, status=201)
            #return JsonResponse({}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Невірний формат JSON'}, status=400)
        except Exception as e:
            print(f"Помилка при додаванні коментаря: {e}")
            return JsonResponse({'error': 'Не вдалося додати коментар.'}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)

    
def get_popular_topics(request):
    # Отримуємо теми з бази даних, сортуємо їх за лайками у порядку спадання
    topics = Topic.objects.all().order_by('-Likes')  # Поле `likes` повинно бути у вашій моделі
    popular_topics_list = list(topics.values())  # Перетворюємо QuerySet в список словників
    return JsonResponse(popular_topics_list, safe=False)

def comments_list(request, topic_id):
    comments = Comment.objects.filter(Topics_id=topic_id).values('Author', 'Content', 'Likes', 'Dislikes', 'Comments', 'Date', 'Time', 'idComments','ParentId')
    return JsonResponse(list(comments), safe=False)

@csrf_exempt
def update_comment(request, comment_id):
    if request.method == 'POST':
        try:
            # Отримання даних з запиту
            data = json.loads(request.body)
            updated_content = data.get('Content')

            if not updated_content:
                return JsonResponse({'error': 'Текст коментаря не може бути порожнім.'}, status=400)

            # Знаходимо коментар за ID
            comment = Comment.objects.get(idComments=comment_id)

            # Оновлюємо текст коментаря
            comment.Content = updated_content
            comment.save()

            return JsonResponse({'message': 'Коментар успішно оновлено.'}, status=200)

        except Comment.DoesNotExist:
            return JsonResponse({'error': 'Коментар не знайдено.'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Невірний формат запиту.'}, status=400)
    else:
        return JsonResponse({'error': 'Метод не дозволений.'}, status=405)

@csrf_exempt
def edit_comment(request, comment_id):
    if request.method == 'POST':
        try:
            # Отримання даних з запиту
            data = json.loads(request.body)
            updated_content = data.get('Content')
            user = data.get('User')

            if not updated_content:
                return JsonResponse({'error': 'Текст коментаря не може бути порожнім.'}, status=400)

            # Знаходимо коментар за ID
            comment = Comment.objects.get(idComments=comment_id)
            if user == comment.Author:
                # Оновлюємо текст коментаря
                comment.Content = updated_content
                comment.save()
                return JsonResponse({'message': 'Коментар успішно оновлено.'}, status=200)
            else:
                return JsonResponse({'message': 'Ви не автор коментаря.'}, status=200)

        except Comment.DoesNotExist:
            return JsonResponse({'error': 'Коментар не знайдено.'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Невірний формат запиту.'}, status=400)
    else:
        return JsonResponse({'error': 'Метод не дозволений.'}, status=405)
    
def delete_comment(request, comment_id):
    # Перевіряємо, чи це POST запит
    if request.method == 'POST':
        data = json.loads(request.body)
        user = data.get('username')
        topic_id = data.get('topicId')
        comment = get_object_or_404(Comment, idComments=comment_id)
        topic = get_object_or_404(Topic, idTopic =topic_id)
        topic.Comments = int(topic.Comments) -1
        topic.save()
        if comment.Author == user:  # Перевіряємо, чи це автор теми
            comment.delete()  # Видаляємо тему
            return redirect('forum_main')  # Перенаправляємо на список тем
        else:
            return redirect('forum_main')  # Якщо не автор, перенаправляємо на головну
    return JsonResponse({'error': 'Method not allowed. Use POST.'}, status=405)