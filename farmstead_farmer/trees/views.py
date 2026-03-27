from django.shortcuts import get_object_or_404, render

from .models import Cutting, Disease, Fertilizer, Planting, Sort, Tree


def sort_detail(request, tree_id, sort_id):
    # Спочатку отримуємо основні дані
    try:
        tree = get_object_or_404(Tree, idTree=tree_id)
        sort = get_object_or_404(Sort, idSort=sort_id, tree_id=tree_id)
    except Exception as e:
        print(f"Помилка при отриманні дерева/сорту: {e}")
        return render(request, 'trees/sort_detail.html', {'tree': None, 'sort': None})

    # Отримуємо додаткові дані окремо, щоб помилки в них не блокували сторінку
    try:
        cutting = list(Cutting.objects.all())
    except Exception as e:
        print(f"Помилка при отриманні Cutting: {e}")
        cutting = []

    try:
        fertilizer = list(Fertilizer.objects.all())
    except Exception as e:
        print(f"Помилка при отриманні Fertilizer: {e}")
        fertilizer = []

    try:
        disease = list(Disease.objects.all())
    except Exception as e:
        print(f"Помилка при отриманні Disease: {e}")
        disease = []

    try:
        planting = list(Planting.objects.all())
    except Exception as e:
        print(f"Помилка при отриманні Planting: {e}")
        planting = []

    return render(request, 'trees/sort_detail.html', {
        'tree': tree,
        'sort': sort,
        'cuttings': cutting,
        'fertilizers': fertilizer,
        'diseases': disease,
        'plantings': planting,
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
