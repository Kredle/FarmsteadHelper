from django.shortcuts import render, get_object_or_404
from .models import Animal

# Відображення списку тварин
def animal_list(request):
    animals = Animal.objects.all()
    return render(request, 'animals/animal_list.html', {'animals': animals})

# Відображення деталей конкретної тварини
def animal_detail(request, id):
    animal = get_object_or_404(Animal, id=id)
    return render(request, 'animals/animal_detail.html', {'animal': animal})
