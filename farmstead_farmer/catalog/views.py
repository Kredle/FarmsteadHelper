import random
from django.shortcuts import render
from .models import Animal, Plant, FindVeg_sort, FindTree_sort, FindTree, FindVeg, Tree, Vegetable
from django.http import JsonResponse
from django.db.models import Q
def search_api(request):
    try:
        query = request.GET.get('query', '').strip().lower()
        
        if not query:
            return JsonResponse({'results': []})
        
        # Пошук у всіх таблицях
        trees = FindTree.objects.filter(Q(common_name2__icontains=query))
        flowers = Plant.objects.filter(Q(common_name__icontains=query))
        animals = Animal.objects.filter(Q(common_name__icontains=query))
        vegetables = FindVeg.objects.filter(Q(common_name2__icontains=query))
        tree_sorts = FindTree_sort.objects.filter(Q(common_name__icontains=query))
        veg_sorts = FindVeg_sort.objects.filter(Q(common_name__icontains=query))
        
        # Формування результатів
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
                'image_url': veg_sort.image_url if veg_sort.image_url else '',  # Виправлено
                'url': f'/catalog/vegetables/{veg_sort.idVeg}/{veg_sort.idVeg_sort}'
            })

        for tree_sort in tree_sorts:
            results.append({
                'type': 'Дерево',
                'name': tree_sort.common_name,
                'image_url': tree_sort.image_url if tree_sort.image_url else '',
                'url': f'/catalog/trees/{tree_sort.idTree}/{tree_sort.idTree_sort}'  # Виправлено
            })
        
        return JsonResponse({'results': results})
    
    except Exception as e:
        # Логування помилки
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