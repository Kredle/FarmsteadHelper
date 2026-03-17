from django.shortcuts import get_object_or_404, render

from .models import DiseasesVeg, FertilizerVeg, SortsVeg, Vegetables


def sort_detail(request, veg_id, sort_id):
    try:
        vegetable = get_object_or_404(Vegetables, idVeg=veg_id)
        sort = get_object_or_404(SortsVeg, idSort=sort_id, vegetables_idVeg_id=veg_id)
        fertilizers = list(FertilizerVeg.objects.all())
        diseases = list(DiseasesVeg.objects.all())
    except Exception:
        vegetable = None
        sort = None
        fertilizers = []
        diseases = []
    return render(request, 'vegetables/sort_detail.html', {
        'vegetable': vegetable,
        'sort': sort,
        'fertilizers': fertilizers,
        'diseases': diseases,
    })


def vegetable_list(request):
    try:
        vegs = list(Vegetables.objects.all())
    except Exception:
        vegs = []
    return render(request, 'vegetables/vegetable_list.html', {'vegs': vegs})


def vegetable_sorts(request, veg_id):
    try:
        veg = get_object_or_404(Vegetables, idVeg=veg_id)
        sorts = list(SortsVeg.objects.filter(vegetables_idVeg_id=veg_id))
    except Exception:
        veg = None
        sorts = []
    return render(request, 'vegetables/sort_list.html', {'veg': veg, 'sorts': sorts})
