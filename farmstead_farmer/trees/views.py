from django.shortcuts import get_object_or_404, render

from .models import Cutting, Disease, Fertilizer, Planting, Sort, Tree


def sort_detail(request, tree_id, sort_id):
    try:
        tree = get_object_or_404(Tree, idTree=tree_id)
        sort = get_object_or_404(Sort, idSort=sort_id, tree_id=tree_id)
        cutting = list(Cutting.objects.all())
        fertilizer = list(Fertilizer.objects.all())
        disease = list(Disease.objects.all())
        planting = list(Planting.objects.all())
    except Exception:
        tree = None
        sort = None
        cutting = []
        fertilizer = []
        disease = []
        planting = []
    return render(request, 'trees/sort_detail.html', {
        'tree': tree,
        'sort': sort,
        'cutting': cutting,
        'fertilizer': fertilizer,
        'disease': disease,
        'planting': planting,
    })


def tree_sorts(request, tree_id):
    try:
        tree = get_object_or_404(Tree, idTree=tree_id)
        sorts = list(Sort.objects.filter(tree_id=tree_id))
    except Exception:
        tree = None
        sorts = []
    return render(request, 'trees/sorts_list.html', {'tree': tree, 'sorts': sorts})


def tree_list(request):
    try:
        trees = list(Tree.objects.all())
    except Exception:
        trees = []
    return render(request, 'trees/trees_main_list.html', {'trees': trees})
