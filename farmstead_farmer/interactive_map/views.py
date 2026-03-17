import json

from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.decorators import throttle_classes
from rest_framework.throttling import UserRateThrottle

from core.application.map import MapUseCase
from core.infrastructure.map_repositories import DjangoMapRepository


class MapTrottle(UserRateThrottle):
    rate = '50/minute'


map_use_case = MapUseCase(DjangoMapRepository())


def map_overview(request):
    return render(request, 'map_overview.html')


def map_view(request):
    return render(request, 'map_canvas.html')


@throttle_classes([MapTrottle])
def save_map(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        user_id = data.get('Author')
        content = data.get('Content')
        if not user_id or not content:
            return JsonResponse({'error': 'User_id and data are required'}, status=400)
        return JsonResponse(map_use_case.save_map(user_id, content), status=201)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as error:
        text = str(error)
        if 'matching query does not exist' in text.lower():
            return JsonResponse({'error': 'User not found'}, status=404)
        return JsonResponse({'error': text}, status=400)


@throttle_classes([MapTrottle])
def update_map(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        user_id = data.get('Author')
        content = data.get('Content')
        if not user_id or not content:
            return JsonResponse({'error': 'User_id and data are required'}, status=400)
        return JsonResponse(map_use_case.update_map(user_id, content), status=201)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as error:
        text = str(error)
        if 'matching query does not exist' in text.lower():
            return JsonResponse({'error': 'User not found'}, status=404)
        return JsonResponse({'error': text}, status=400)


@throttle_classes([MapTrottle])
def check_map(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    try:
        data = json.loads(request.body)
        user_id = data.get('Author')
        if not user_id:
            return JsonResponse({'error': 'User_id is required'}, status=400)
        return JsonResponse(map_use_case.check_map(user_id), status=201)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as error:
        text = str(error)
        if 'matching query does not exist' in text.lower():
            return JsonResponse({'error': 'User not found'}, status=404)
        return JsonResponse({'error': text}, status=400)


@throttle_classes([MapTrottle])
def get_map(request, user_id):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    try:
        return JsonResponse(map_use_case.get_map(user_id), status=200)
    except Exception as error:
        text = str(error)
        if 'matching query does not exist' in text.lower():
            return JsonResponse({'error': 'User not found'}, status=404)
        return JsonResponse({'error': text}, status=400)


@throttle_classes([MapTrottle])
def get_tree_sorts(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не дозволено'}, status=405)

    try:
        return JsonResponse(map_use_case.tree_sorts(), safe=False)
    except Exception as error:
        return JsonResponse({'error': f'Помилка при обробці запиту: {str(error)}'}, status=500)


@throttle_classes([MapTrottle])
def get_vegetable_sorts(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не дозволено'}, status=405)

    try:
        return JsonResponse(map_use_case.vegetable_sorts(), safe=False)
    except Exception as error:
        return JsonResponse({'error': f'Помилка при обробці запиту: {str(error)}'}, status=500)
