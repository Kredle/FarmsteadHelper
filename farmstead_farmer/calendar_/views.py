from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.throttling import UserRateThrottle

from core.application.calendar_app import CalendarUseCase
from core.infrastructure.calendar_repositories import (
    DjangoCalendarRepository, CategoryNotFoundError, SortNotFoundError,
)


class GetSortsAndDetailsTrottle(UserRateThrottle):
    rate = '30/minute'


_calendar_repo = DjangoCalendarRepository()
calendar_use_case = CalendarUseCase(_calendar_repo)


@throttle_classes([GetSortsAndDetailsTrottle])
@api_view(['POST'])
def get_sorts(request):
    try:
        category = request.data.get('category', '')
        sorts = calendar_use_case.get_sorts(category)
        return JsonResponse(sorts, safe=False)
    except CategoryNotFoundError:
        return JsonResponse({'error': 'Unknown category'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def calendar(request):
    return render(request, 'calendar.html')


@throttle_classes([GetSortsAndDetailsTrottle])
@api_view(['POST'])
def get_sort_details(request):
    try:
        category = request.data.get('category', '')
        sort_name = request.data.get('sort_name', '')
        values = calendar_use_case.get_sort_details(category, sort_name)
        return JsonResponse(values)
    except CategoryNotFoundError:
        return JsonResponse({'error': 'Unknown category'}, status=400)
    except SortNotFoundError as e:
        return JsonResponse({'error': str(e)}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
