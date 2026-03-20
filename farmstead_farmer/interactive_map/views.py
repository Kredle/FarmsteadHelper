import json

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
from rest_framework.decorators import throttle_classes
from rest_framework.throttling import UserRateThrottle

from api.models import CustomUser
from core.application.map import MapUseCase
from core.infrastructure.map_repositories import DjangoMapRepository
from core.infrastructure.repositories import DjangoUserRepository
from interactive_map.models import Map


class MapTrottle(UserRateThrottle):
    rate = '50/minute'


map_use_case = MapUseCase(DjangoMapRepository())
user_repository = DjangoUserRepository()


def _get_user_from_request_token(request):
    token = request.GET.get('token')
    if not token:
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Token '):
            token = auth_header.replace('Token ', '', 1).strip()
        elif auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '', 1).strip()
    return user_repository.find_by_token(token)


def map_overview(request):
    return render(request, 'map_overview.html')


def map_subscription(request):
    return render(
        request,
        'map_subscription.html',
        {
            'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
            'status': request.GET.get('status', ''),
        },
    )


def map_view(request):
    viewer = _get_user_from_request_token(request)

    owner_id_param = request.GET.get('owner_id')
    map_id_param = request.GET.get('map_id')
    owner_id = viewer.id if viewer is not None else None
    map_id = None

    if owner_id_param:
        try:
            owner_id = int(owner_id_param)
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Invalid owner_id'}, status=400)

    if map_id_param:
        try:
            map_id = int(map_id_param)
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Invalid map_id'}, status=400)

    if owner_id is None:
        return redirect('/login/')

    map_data = None
    current_map_id = ''
    if owner_id is not None:
        snapshot = map_use_case.get_map(owner_id, map_id=map_id)
        map_data = snapshot.get('map_data')
        current_map_id = snapshot.get('map_id') or ''
        if map_data is not None and not isinstance(map_data, str):
            map_data = json.dumps(map_data, ensure_ascii=False)

    return render(
        request,
        'map_canvas.html',
        {
            'owner_id': owner_id or '',
            'map_data': map_data,
            'current_map_id': current_map_id,
            'has_active_subscription': bool(viewer and viewer.has_active_subscription),
        },
    )


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

        user = CustomUser.objects.filter(id=user_id).first()
        if user is None:
            return JsonResponse({'error': 'User not found'}, status=404)

        map_count = Map.objects.filter(User_id=user).count()
        if map_count >= 1 and not user.has_active_subscription:
            return JsonResponse(
                {'error': 'Для створення декількох мап потрібна активна передплата.'},
                status=403,
            )

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
        map_id = data.get('MapId')
        if not user_id or not content:
            return JsonResponse({'error': 'User_id and data are required'}, status=400)

        if map_id is not None:
            try:
                map_id = int(map_id)
            except (TypeError, ValueError):
                return JsonResponse({'error': 'Invalid MapId'}, status=400)

        return JsonResponse(map_use_case.update_map(user_id, content, map_id=map_id), status=201)
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

        user = CustomUser.objects.filter(id=user_id).first()
        if user is None:
            return JsonResponse({'error': 'User not found'}, status=404)

        latest_map = Map.objects.filter(User_id=user).order_by('-id').first()
        payload = {
            'status': 'success',
            'exists': latest_map is not None,
            'count': Map.objects.filter(User_id=user).count(),
            'latest_map_id': int(latest_map.id) if latest_map else None,
            'has_active_subscription': user.has_active_subscription,
        }
        return JsonResponse(payload, status=201)
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
        map_id_param = request.GET.get('map_id')
        map_id = int(map_id_param) if map_id_param else None
        return JsonResponse(map_use_case.get_map(user_id, map_id=map_id), status=200)
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


@throttle_classes([MapTrottle])
def get_compatibility_index(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Метод не дозволено'}, status=405)

    try:
        return JsonResponse(map_use_case.compatibility_index(), safe=False)
    except Exception as error:
        return JsonResponse({'error': f'Помилка при обробці запиту: {str(error)}'}, status=500)
