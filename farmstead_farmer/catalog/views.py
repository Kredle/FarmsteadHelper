import random
from django.shortcuts import render
from .models import Animal, Plant, FindVeg_sort, FindTree_sort, FindTree, FindVeg, Tree, Vegetable
from django.http import JsonResponse
from django.db.models import Q
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework import status
import traceback
from rest_framework.throttling import UserRateThrottle

class CatalogTrottle(UserRateThrottle):
    rate = '40/minute'

@throttle_classes([CatalogTrottle])
def search_api(request):
    try:
        query = request.GET.get('query', '').strip().lower()
        
        if not query:
            return JsonResponse({'results': []})
        
        trees = FindTree.objects.filter(Q(common_name2__icontains=query))
        flowers = Plant.objects.filter(Q(common_name__icontains=query))
        animals = Animal.objects.filter(Q(common_name__icontains=query))
        vegetables = FindVeg.objects.filter(Q(common_name2__icontains=query))
        tree_sorts = FindTree_sort.objects.filter(Q(common_name__icontains=query))
        veg_sorts = FindVeg_sort.objects.filter(Q(common_name__icontains=query))
        
        results = []
        for tree in trees:
            results.append({
                'type': 'Дерево',
                'name': tree.common_name2,
                'image_url': tree.image_url if tree.image_url else '',
                'url': f'/catalog/trees/{tree.idTree}'
            })
        
        for flower in flowers:
            results.append({
                'type': 'Квітка',
                'name': flower.common_name,
                'image_url': flower.image_url if flower.image_url else '',
                'url': f'/catalog/flowers/{flower.sort_id}'
            })
        
        for animal in animals:
            results.append({
                'type': 'Тварина',
                'name': animal.common_name,
                'image_url': animal.image_url if animal.image_url else '',
                'url': f'/catalog/animals/{animal.sort_id}'
            })
        
        for vegetable in vegetables:
            results.append({
                'type': 'Овоч',
                'name': vegetable.common_name2,
                'image_url': vegetable.image_url if vegetable.image_url else '',
                'url': f'/catalog/vegetables/{vegetable.idVeg}'
            })

        for veg_sort in veg_sorts:
            results.append({
                'type': 'Овоч',
                'name': veg_sort.common_name,
                'image_url': veg_sort.image_url if veg_sort.image_url else '',  
                'url': f'/catalog/vegetables/{veg_sort.idVeg}/{veg_sort.idVeg_sort}'
            })

        for tree_sort in tree_sorts:
            results.append({
                'type': 'Дерево',
                'name': tree_sort.common_name,
                'image_url': tree_sort.image_url if tree_sort.image_url else '',
                'url': f'/catalog/trees/{tree_sort.idTree}/{tree_sort.idTree_sort}'
            })
        
        return JsonResponse({'results': results})
    
    except Exception as e:
        print(f"Помилка: {e}")
        return JsonResponse({'error': 'Internal Server Error'}, status=500)
def catalog_view(request):
    try:
        animals = list(Animal.objects.all())
        plants = list(Plant.objects.all())
        vegetables = list(Vegetable.objects.filter(vegetable__isnull=False))
        trees = list(Tree.objects.filter(tree__isnull=False))

        all_items = animals + plants + vegetables + trees
        random.shuffle(all_items)
        items_to_display = all_items[:9]

        for item in items_to_display:
            if item.category in ['animals', 'flowers']:
                item.url = f'/catalog/{item.category}/{item.sort_id}'
            elif item.category == 'vegetables':
                item.url = f'/catalog/{item.category}/{item.vegetable.id}/{item.sort_id}'
            elif item.category == 'trees':
                item.url = f'/catalog/{item.category}/{item.tree.id}/{item.sort_id}'

        context = {
            'items': items_to_display,
        }
        return render(request, 'catalog/catalog.html', context)
    except Exception as e:
        animals = list(Animal.objects.all())
        plants = list(Plant.objects.all())

        all_items = animals + plants
        random.shuffle(all_items)
        items_to_display = all_items[:9]

        for item in items_to_display:
            item.url = f'/catalog/{item.category}/{item.sort_id}'
        
        context = {
            'items': items_to_display,
        }
        return render(request, 'catalog/catalog.html', context)


@throttle_classes([CatalogTrottle])
@api_view(['POST'])
def filter_catalog_api(request):
    try:
        selected_categories = request.data.get('categories', [])
        allowed_categories = {'animals', 'flowers', 'vegetables', 'trees'}
        selected_categories = [cat for cat in selected_categories if cat in allowed_categories]

        all_items = []
        
        if 'animals' in selected_categories:
            all_items.extend(Animal.objects.all())
        
        if 'flowers' in selected_categories:
            all_items.extend(Plant.objects.all())
        
        if 'vegetables' in selected_categories:
            all_items.extend(Vegetable.objects.filter(vegetable__isnull=False))
        
        if 'trees' in selected_categories:
            all_items.extend(Tree.objects.filter(tree__isnull=False))

        random.shuffle(all_items)
        items_to_display = all_items[:9]

        results = []
        for item in items_to_display:
            if isinstance(item, Animal):
                results.append({
                    'category': 'animals',
                    'common_name': item.common_name,
                    'image_url': item.image_url or '',
                    'url': f'/catalog/animals/{item.sort_id}'
                })
            elif isinstance(item, Plant):
                results.append({
                    'category': 'flowers',
                    'common_name': item.common_name,
                    'image_url': item.image_url or '',
                    'url': f'/catalog/flowers/{item.sort_id}'
                })
            elif isinstance(item, Vegetable):
                results.append({
                    'category': 'vegetables',
                    'common_name': item.common_name,
                    'image_url': item.image_url or '',
                    'url': f'/catalog/vegetables/{item.vegetable.id}/{item.sort_id}' 
                })
            elif isinstance(item, Tree):
                results.append({
                    'category': 'trees',
                    'common_name': item.common_name,
                    'image_url': item.image_url or '',
                    'url': f'/catalog/trees/{item.tree.id}/{item.sort_id}' 
                })

        return Response({'items': results})

    except Exception as e:
        print(f"Помилка: {str(e)}\n{traceback.format_exc()}")
        return Response({'error': 'Помилка сервера'}, status=500)
