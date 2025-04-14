from django.shortcuts import render, redirect
import json
from django.http import JsonResponse
from .models import Map
from trees.models import Tree, Sort
from vegetables.models import Vegetables, SortsVeg
from api.models import CustomUser
from django.views.decorators.csrf import csrf_exempt
from rest_framework.throttling import UserRateThrottle
from rest_framework.decorators import throttle_classes

class MapTrottle(UserRateThrottle):
    rate = '50/minute'

def map_overview(request):
    return render(request, 'map_overview.html')

def map_view(request):
    return render(request, "map_canvas.html")

@throttle_classes([MapTrottle])
def save_map(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('Author')
            content = data.get('Content')  # це вже Python-словник
            if not user_id or not content:
                return JsonResponse({'error': 'User_id and data are required'}, status=400)

            # Перевірка користувача
            try:
                author = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)

            # Оновлюємо статус мапи у користувача
            author.has_map = True
            author.save()

            # Зберігаємо карту (перетворюємо в JSON-рядок перед записом)
            new_map = Map(
                User_id=author,
                data=json.dumps(content)
            )
            new_map.save()  # ← це обов'язково

            return JsonResponse({
                'status': 'success',
                'message': 'Map saved successfully',
                'map_id': new_map.id
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@throttle_classes([MapTrottle])
def update_map(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('Author')
            content = data.get('Content')  # це вже Python-словник
            if not user_id or not content:
                return JsonResponse({'error': 'User_id and data are required'}, status=400)

            # Перевірка користувача
            try:
                author = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)

            # Оновлюємо статус мапи у користувача
            author.has_map = True
            author.save()

            # Зберігаємо карту (перетворюємо в JSON-рядок перед записом)
            map = Map.objects.get(User_id=author)
            map.data = json.dumps(content)
            map.save()  # ← це обов'язково

            return JsonResponse({
                'status': 'success',
                'message': 'Map saved successfully',
                'map_id': map.id
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@throttle_classes([MapTrottle])
def check_map(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('Author')
            author = CustomUser.objects.get(id=user_id)
            map = Map.objects.filter(User_id=author).first()
            if map is None:
                return JsonResponse({'status': 'success', 'exists': False}, status=201)
            else:
                return JsonResponse({'status': 'success', 'exists': True}, status=201)
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@throttle_classes([MapTrottle])
def get_map(request, user_id):
    if request.method == 'GET':
        try:
            author = CustomUser.objects.get(id=user_id)
            #print(f"author: {author.id}")
            map = Map.objects.filter(User_id=author).first()
            #print(f"map: {map.data}")
            if map is None:
                return render(request, 'map_overview.html')  # Повертаємо сторінку без мапи
            else:
                # Повертаємо сторінку з мапою та передаємо дані мапи
                return render(request, 'map_canvas.html', {'map_data': map.data, 'owner_id': author.id})
                #return redirect(f"/map/map/?map_data={map.data}")
                #return JsonResponse({
                #    'map_data': map.data
                #}, status=201)
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@throttle_classes([MapTrottle])
def get_tree_sorts(request):
    if request.method == 'POST':
        try:
            # Отримуємо всі дерева з їхніми сортами
            trees = Tree.objects.all()
            tree_data = []

            for tree in trees:
                # Для кожного дерева отримуємо всі сорти
                sorts = tree.sorts.all()  # Використовуємо related_name 'sorts'
                sorts_data = [{"id": Sort.idSort, "sort": Sort.sort} for Sort in sorts]
                
                tree_data.append({
                    "id": tree.idTree,
                    "name": tree.name,
                    "sorts": sorts_data  # Додаємо сорти до дерева
                })
            
            return JsonResponse(tree_data, safe=False)

        except Exception as e:
            return JsonResponse({"error": f"Помилка при обробці запиту: {str(e)}"}, status=500)
    else:
        return JsonResponse({"error": "Метод не дозволено"}, status=405)

@throttle_classes([MapTrottle])
def get_vegetable_sorts(request):
    if request.method == 'POST':
        try:
            # Отримуємо всі овочі з їхніми сортами
            vegetables = Vegetables.objects.all()
            vegetable_data = []

            for vegetable in vegetables:
                # Для кожного овоча отримуємо всі сорти
                sortsVeg = vegetable.sorts_veg.all()  # Використовуємо related_name 'sorts'
                sortsVeg_data = [{"idSort": SortVeg.idSort, "Name": SortVeg.Name} for SortVeg in sortsVeg]
                
                vegetable_data.append({
                    "idVeg": vegetable.idVeg,
                    "Name": vegetable.Name,
                    "sortsVeg": sortsVeg_data  # Додаємо сорти до овоча
                })
            
            return JsonResponse(vegetable_data, safe=False)

        except Exception as e:
            return JsonResponse({"error": f"Помилка при обробці запиту: {str(e)}"}, status=500)
    else:
        return JsonResponse({"error": "Метод не дозволено"}, status=405)