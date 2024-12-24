from django.shortcuts import render, get_object_or_404
from .models import SortsVeg, FertilizerVeg, DiseasesVeg, Vegetables

def sort_detail(request, id):
    sort = SortsVeg.objects.get(idSort=id) 
    vegetable = sort.vegetables_idVeg  
    fertilizers = FertilizerVeg.objects.all()
    diseases = DiseasesVeg.objects.all()

    context = {
        'vegetable': vegetable,
        'sort': sort,
        'fertilizers': fertilizers,
        'diseases': diseases,
    }

    return render(request, 'vegetables/vegetable_detail.html', context)

def vegetable_list(request):
    sorts = SortsVeg.objects.all() 
    return render(request, 'vegetables/vegetable_list.html', {'sorts': sorts})
