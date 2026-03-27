import json

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
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


def _get_user_from_payload_token(request, payload: dict | None = None):
    payload = payload or {}
    token = str(payload.get('token') or '').strip()
    if not token:
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Token '):
            token = auth_header.replace('Token ', '', 1).strip()
        elif auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '', 1).strip()
    if not token:
        return None
    return user_repository.find_by_token(token)


def _is_map_private(map_obj: Map) -> bool:
    return bool(getattr(map_obj, 'is_private', False))


def _can_manage_map(actor: CustomUser | None, map_obj: Map) -> bool:
    if actor is None:
        return False
    is_admin = bool(actor.is_superuser or actor.is_staff)
    owner_id = int(getattr(map_obj, 'User_id_id', 0) or 0)
    return is_admin or int(actor.id) == owner_id


def _serialize_map_item(map_obj: Map, can_manage: bool) -> dict:
    map_name = str(getattr(map_obj, 'map_name', '') or '').strip()
    if not map_name:
        map_name = f'Мапа #{int(map_obj.id)}'
    return {
        'map_id': int(map_obj.id),
        'map_name': map_name,
        'is_private': _is_map_private(map_obj),
        'can_manage': bool(can_manage),
    }


@ensure_csrf_cookie
def map_overview(request):
    return render(request, 'map_overview.html')


@ensure_csrf_cookie
def map_my_maps(request):
    return render(request, 'map_my_maps.html')


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
    create_new_flag = str(request.GET.get('create_new') or '').strip().lower() in {'1', 'true', 'yes'}
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

    owner_user = CustomUser.objects.filter(id=owner_id).first()
    if owner_user is None:
        return JsonResponse({'error': 'User not found'}, status=404)

    is_owner = viewer is not None and int(viewer.id) == int(owner_id)
    is_admin = bool(viewer and (viewer.is_superuser or viewer.is_staff))

    if not is_owner and not is_admin:
        if map_id is not None:
            requested_map = Map.objects.filter(User_id=owner_user, id=map_id).first()
            if requested_map is None:
                return JsonResponse({'error': 'Map not found'}, status=404)
            if _is_map_private(requested_map):
                return JsonResponse({'error': 'Map is private'}, status=403)
        else:
            public_map = None
            for candidate in Map.objects.filter(User_id=owner_user).order_by('-id'):
                if not _is_map_private(candidate):
                    public_map = candidate
                    break
            if public_map is None:
                return JsonResponse({'error': 'No public maps available'}, status=403)
            map_id = int(public_map.id)

    if viewer is not None and int(viewer.id) == int(owner_id) and (not viewer.has_active_subscription):
        user_maps = list(Map.objects.filter(User_id=viewer).order_by('-id').values_list('id', flat=True))
        if map_id is not None:
            if not user_maps:
                return redirect('/map/subscription/')
            latest_map_id = int(user_maps[0])
            requested_map_id = int(map_id)

            # Без передплати не дозволяємо відкривати інші мапи по прямому URL.
            if requested_map_id != latest_map_id:
                return redirect('/map/subscription/')

    map_data = None
    current_map_id = ''
    snapshot = {'map_name': ''}
    owner_has_active_subscription = False
    owner_map_count = 0
    if owner_id is not None:
        # Explicit "create new" mode should open an empty workspace, not the latest existing map.
        if not (create_new_flag and viewer is not None and int(viewer.id) == int(owner_id)):
            snapshot = map_use_case.get_map(owner_id, map_id=map_id)
            map_data = snapshot.get('map_data')
            current_map_id = snapshot.get('map_id') or ''
            if map_data is not None and not isinstance(map_data, str):
                map_data = json.dumps(map_data, ensure_ascii=False)

        owner_has_active_subscription = bool(owner_user and owner_user.has_active_subscription)
        owner_map_count = Map.objects.filter(User_id=owner_user).count() if owner_user else 0

    return render(
        request,
        'map_canvas.html',
        {
            'owner_id': owner_id or '',
            'map_data': map_data,
            'current_map_id': current_map_id,
            'current_map_name': snapshot.get('map_name') or '',
            'has_active_subscription': bool(viewer and viewer.has_active_subscription),
            'owner_has_active_subscription': owner_has_active_subscription,
            'owner_map_count': owner_map_count,
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
        map_name = str(data.get('MapName') or '').strip()
        if not user_id or not content:
            return JsonResponse({'error': 'User_id and data are required'}, status=400)

        if not map_name:
            return JsonResponse({'error': 'Map name is required'}, status=400)

        user = CustomUser.objects.filter(id=user_id).first()
        if user is None:
            return JsonResponse({'error': 'User not found'}, status=404)

        actor = _get_user_from_payload_token(request, data)
        if actor is None:
            return JsonResponse({'error': 'Invalid or missing token'}, status=401)

        if int(actor.id) != int(user.id) and not (actor.is_superuser or actor.is_staff):
            return JsonResponse({'error': 'Forbidden'}, status=403)

        map_count = Map.objects.filter(User_id=user).count()
        if map_count >= 1 and not user.has_active_subscription:
            return JsonResponse(
                {'error': 'Для створення декількох мап потрібна активна передплата.'},
                status=403,
            )

        return JsonResponse(map_use_case.save_map(user_id, content, map_name=map_name), status=201)
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
        map_name = str(data.get('MapName') or '').strip()
        map_id = data.get('MapId')
        if not user_id or not content:
            return JsonResponse({'error': 'User_id and data are required'}, status=400)

        if map_id is not None:
            try:
                map_id = int(map_id)
            except (TypeError, ValueError):
                return JsonResponse({'error': 'Invalid MapId'}, status=400)

        user = CustomUser.objects.filter(id=user_id).first()
        if user is None:
            return JsonResponse({'error': 'User not found'}, status=404)

        actor = _get_user_from_payload_token(request, data)
        if actor is None:
            return JsonResponse({'error': 'Invalid or missing token'}, status=401)

        if int(actor.id) != int(user.id) and not (actor.is_superuser or actor.is_staff):
            return JsonResponse({'error': 'Forbidden'}, status=403)

        return JsonResponse(map_use_case.update_map(user_id, content, map_id=map_id, map_name=map_name or None), status=201)
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
            'latest_map_name': str(getattr(latest_map, 'map_name', '') or '').strip() if latest_map else '',
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
def list_maps(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        user_id = data.get('Author')
        if not user_id:
            return JsonResponse({'error': 'User_id is required'}, status=400)

        owner = CustomUser.objects.filter(id=int(user_id)).first()
        if owner is None:
            return JsonResponse({'error': 'User not found'}, status=404)

        actor = _get_user_from_payload_token(request, data)
        is_owner = bool(actor and int(actor.id) == int(owner.id))
        is_admin = bool(actor and (actor.is_superuser or actor.is_staff))
        can_manage = is_owner or is_admin

        maps = []
        for map_obj in Map.objects.filter(User_id=owner).order_by('-id'):
            is_private = _is_map_private(map_obj)
            if (not can_manage) and is_private:
                continue
            maps.append(_serialize_map_item(map_obj, can_manage=can_manage))

        return JsonResponse({'status': 'success', 'maps': maps}, status=200)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as error:
        text = str(error)
        if 'matching query does not exist' in text.lower():
            return JsonResponse({'error': 'User not found'}, status=404)
        return JsonResponse({'error': text}, status=400)


@throttle_classes([MapTrottle])
def update_map_settings(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        map_id = data.get('MapId')
        map_name = data.get('MapName')
        is_private = data.get('IsPrivate')

        if map_id is None:
            return JsonResponse({'error': 'MapId is required'}, status=400)

        try:
            map_id = int(map_id)
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Invalid MapId'}, status=400)

        if is_private is not None and not isinstance(is_private, bool):
            return JsonResponse({'error': 'IsPrivate must be boolean'}, status=400)

        actor = _get_user_from_payload_token(request, data)
        if actor is None:
            return JsonResponse({'error': 'Invalid or missing token'}, status=401)

        map_obj = Map.objects.filter(id=map_id).first()
        if map_obj is None:
            return JsonResponse({'error': 'Map not found'}, status=404)

        if not _can_manage_map(actor, map_obj):
            return JsonResponse({'error': 'Forbidden'}, status=403)

        owner_id = int(getattr(map_obj, 'User_id_id', 0) or 0)

        return JsonResponse(
            map_use_case.update_map_settings(owner_id, map_id, map_name=map_name, is_private=is_private),
            status=200,
        )
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as error:
        text = str(error)
        if 'map not found' in text.lower():
            return JsonResponse({'error': 'Map not found'}, status=404)
        if 'matching query does not exist' in text.lower():
            return JsonResponse({'error': 'User not found'}, status=404)
        return JsonResponse({'error': text}, status=400)


@throttle_classes([MapTrottle])
def delete_map(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        map_id = data.get('MapId')

        if map_id is None:
            return JsonResponse({'error': 'MapId is required'}, status=400)

        try:
            map_id = int(map_id)
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Invalid MapId'}, status=400)

        actor = _get_user_from_payload_token(request, data)
        if actor is None:
            return JsonResponse({'error': 'Invalid or missing token'}, status=401)

        map_obj = Map.objects.filter(id=map_id).first()
        if map_obj is None:
            return JsonResponse({'error': 'Map not found'}, status=404)

        if not _can_manage_map(actor, map_obj):
            return JsonResponse({'error': 'Forbidden'}, status=403)

        owner_id = int(getattr(map_obj, 'User_id_id', 0) or 0)

        return JsonResponse(map_use_case.delete_map(owner_id, map_id), status=200)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as error:
        text = str(error)
        if 'map not found' in text.lower():
            return JsonResponse({'error': 'Map not found'}, status=404)
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


@throttle_classes([MapTrottle])
def profile_maps(request):
    if request.method not in ('POST', 'GET'):
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        if request.method == 'GET':
            data = {
                'username': request.GET.get('username'),
                'token': request.GET.get('token'),
            }
        else:
            data = json.loads(request.body)
        username = str(data.get('username') or '').strip()
        if not username:
            return JsonResponse({'error': 'username is required'}, status=400)

        owner = CustomUser.objects.filter(username=username).first()
        if owner is None:
            return JsonResponse({'error': 'User not found'}, status=404)

        viewer = _get_user_from_payload_token(request, data)
        is_owner = bool(viewer and int(viewer.id) == int(owner.id))
        is_admin = bool(viewer and (viewer.is_superuser or viewer.is_staff))
        can_manage = is_owner or is_admin

        maps_payload = []
        for map_obj in Map.objects.filter(User_id=owner).order_by('-id'):
            if _is_map_private(map_obj):
                continue
            maps_payload.append(_serialize_map_item(map_obj, can_manage=can_manage))

        return JsonResponse(
            {
                'status': 'success',
                'owner_id': int(owner.id),
                'maps': maps_payload,
            },
            status=200,
        )
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as error:
        return JsonResponse({'error': str(error)}, status=400)
