from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle

from core.application.catalog import CatalogUseCase
from core.infrastructure.catalog_repositories import DjangoCatalogRepository


class CatalogTrottle(UserRateThrottle):
    rate = '40/minute'


catalog_use_case = CatalogUseCase(DjangoCatalogRepository())


@throttle_classes([CatalogTrottle])
@api_view(['GET'])
def search_api(request):
    try:
        query = request.GET.get('query', '')
        return Response(catalog_use_case.search(query))
    except Exception as e:
        print(f"Search error: {e}")
        return Response({'error': str(e)}, status=500)


def catalog_view(request):
    try:
        cards = catalog_use_case.random_cards().get('items', [])
    except Exception:
        cards = []
    return render(request, 'catalog/catalog.html', {'items': cards})


@throttle_classes([CatalogTrottle])
@api_view(['POST'])
def filter_catalog_api(request):
    try:
        return Response(catalog_use_case.filter_cards(request.data.get('categories', [])))
    except Exception:
        return Response({'error': 'Помилка сервера'}, status=500)


@throttle_classes([CatalogTrottle])
def catalog_items_api(request):
    try:
        return JsonResponse(catalog_use_case.random_cards())
    except Exception:
        return JsonResponse({'items': []})


@throttle_classes([CatalogTrottle])
def animals_list_api(request):
    return JsonResponse(catalog_use_case.animals_list(), safe=False)


@throttle_classes([CatalogTrottle])
def animal_sorts_api(request, animal_id):
    return JsonResponse(catalog_use_case.animal_sorts(animal_id))


@throttle_classes([CatalogTrottle])
def animal_detail_api(request, animal_id, sort_id):
    return JsonResponse(catalog_use_case.animal_detail(animal_id, sort_id))
