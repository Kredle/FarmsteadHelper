from django.shortcuts import render, get_object_or_404
from .models import SortsVeg, FertilizerVeg, DiseasesVeg, Vegetables

def sort_detail(request, veg_id, sort_id):
    vegetable = get_object_or_404(Vegetables, idVeg=veg_id)
    sort = get_object_or_404(SortsVeg, idSort=sort_id, vegetables_idVeg=vegetable)
    fertilizers = FertilizerVeg.objects.all()
    diseases = DiseasesVeg.objects.all()

    context = {
        'vegetable': vegetable,
        'sort': sort,
        'fertilizers': fertilizers,
        'diseases': diseases,
    }

    return render(request, 'vegetables/sort_detail.html', context)

def vegetable_list(request):
    vegs = Vegetables.objects.all() 
    return render(request, 'vegetables/vegetable_list.html', {'vegs': vegs})

def vegetable_sorts(request, veg_id):
    veg = get_object_or_404(Vegetables, idVeg=veg_id)
    sorts = SortsVeg.objects.filter(vegetables_idVeg=veg) 
    return render(request, 'vegetables/sort_list.html', {'veg': veg, 'sorts': sorts})
