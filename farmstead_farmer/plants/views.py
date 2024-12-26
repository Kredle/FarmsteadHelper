from django.shortcuts import render, get_object_or_404
from .models import Plant

def plant_list(request):
    plants = Plant.objects.all() 
    return render(request, 'plants/plant_list.html', {'plants': plants})

def plant_detail(request, id):
    plant = get_object_or_404(Plant, id=id)
    return render(request, 'plants/plant_detail.html', {'plant': plant})