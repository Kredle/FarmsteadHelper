import random
from django.shortcuts import render
from .models import Animal, Plant, Vegetable, Tree

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