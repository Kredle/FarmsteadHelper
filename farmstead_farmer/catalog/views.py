import random
from django.shortcuts import render
from .models import Animal, Plant, Vegetable, Tree

def catalog_view(request):
    # Отримуємо всі елементи з бази даних
    animals = list(Animal.objects.all())
    plants = list(Plant.objects.all())
    vegetables = list(Vegetable.objects.all())
    trees = list(Tree.objects.all())

    all_items = animals + plants + vegetables + trees
    random.shuffle(all_items)
    items_to_display = all_items[:9]

    context = {
        'items': items_to_display,
    }
    return render(request, 'catalog/catalog.html', context)