from django.shortcuts import render

from core.application.catalog import CatalogUseCase
from core.infrastructure.catalog_repositories import DjangoCatalogRepository


catalog_use_case = CatalogUseCase(DjangoCatalogRepository())


def animal_list(request):
    try:
        animals = catalog_use_case.animals_list()
    except Exception as e:
        print(f"Error in animal_list: {e}")
        animals = []
    legacy_animals = [
        {
            'idAni': item.get('id'),
            'Name': item.get('name'),
            'Image': item.get('image'),
        }
        for item in animals
    ]
    return render(request, 'animals/animal_list.html', {'animals': legacy_animals})


def animal_detail(request, animal_id, sort_id):
    try:
        detail = catalog_use_case.animal_detail(animal_id, sort_id)
    except Exception as e:
        print(f"Error in animal_detail: {e}")
        detail = {}
    return render(request, 'animals/animal_detail.html', {'animal': detail})


def animal_sorts(request, animal_id):
    try:
        payload = catalog_use_case.animal_sorts(animal_id)
    except Exception as e:
        print(f"Error in animal_sorts: {e}")
        payload = {'animal': {}, 'sorts': []}
    animal = {
        'idAni': payload.get('animal', {}).get('id'),
        'Name': payload.get('animal', {}).get('name'),
        'Image': payload.get('animal', {}).get('image'),
    }
    sorts = [
        {
            'id': sort.get('id'),
            'common_name': sort.get('name'),
            'sort': sort.get('name'),
            'image': sort.get('image'),
        }
        for sort in payload.get('sorts', [])
    ]
    return render(request, 'animals/animal_sorts_list.html', {'animal': animal, 'sorts': sorts})
