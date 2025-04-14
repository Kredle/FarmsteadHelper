from django.shortcuts import render, get_object_or_404
from .models import Animal, Animal_main

# Відображення списку тварин
def animal_list(request):
    animals = Animal_main.objects.all()
    return render(request, 'animals/animal_list.html', {'animals': animals})


def animal_detail(request, animal_id, sort_id):
    animal = get_object_or_404(Animal_main, idAni=animal_id)
    sort = get_object_or_404(Animal, id=sort_id, animal_idAni=animal)

    return render(request, 'animals/animal_detail.html', {'animal': sort})

def animal_sorts(request, animal_id):
    animal = get_object_or_404(Animal_main, idAni=animal_id)
    sorts = animal.sorts.all()
    return render(request, 'animals/animal_sorts_list.html', {'animal': animal, 'sorts': sorts})