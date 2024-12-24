from django.shortcuts import render, get_object_or_404
from .models import Sort, Tree, Cutting, Fertilizer, Disease, Planting

def sort_detail(request, id):
    sort = Sort.objects.get(idSort=id) 
    tree = sort.tree  
    cuttings = Cutting.objects.all()
    fertilizers = Fertilizer.objects.all()
    diseases = Disease.objects.all()
    plantings = Planting.objects.all()

    context = {
        'tree': tree,
        'sort': sort,
        'cuttings': cuttings,
        'fertilizers': fertilizers,
        'diseases': diseases,
        'plantings': plantings,
    }

    return render(request, 'trees/tree_detail.html', context)



def tree_list(request):
    sorts = Sort.objects.all() 
    return render(request, 'trees/trees_list.html', {'sorts': sorts})
