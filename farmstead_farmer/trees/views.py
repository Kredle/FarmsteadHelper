from django.shortcuts import render, get_object_or_404
from .models import Sort, Tree, Cutting, Fertilizer, Disease, Planting

def sort_detail(request, tree_id, sort_id):
    tree = get_object_or_404(Tree, idTree=tree_id)
    sort = get_object_or_404(Sort, idSort=sort_id, tree=tree)
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

    return render(request, 'trees/sort_detail.html', context)



def tree_sorts(request, tree_id):
    tree = get_object_or_404(Tree, idTree=tree_id)
    sorts = tree.sorts.all()
    return render(request, 'trees/sorts_list.html', {'tree': tree, 'sorts': sorts})

def tree_list(request):
    trees = Tree.objects.all() 
    return render(request, 'trees/trees_main_list.html', {'trees': trees})
