from django.shortcuts import get_object_or_404, render

from .models import Plant


def plant_list(request):
    try:
        plants = list(Plant.objects.all())
    except Exception:
        plants = []
    return render(request, 'plants/plant_list.html', {'plants': plants})


def plant_detail(request, id):
    try:
        plant = get_object_or_404(Plant, id=id)
    except Exception:
        plant = None
    return render(request, 'plants/plant_detail.html', {'plant': plant})