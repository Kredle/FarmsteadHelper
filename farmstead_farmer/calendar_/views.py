from django.http import JsonResponse
from rest_framework.decorators import api_view, throttle_classes
from .models import Sort_tree, Sort_veg, Plants, Veg, Tree, Cutting, Planting, Fertilizer, Fertilizer_veg
import json
from django.shortcuts import render
from rest_framework.throttling import UserRateThrottle

class GetSortsAndDetailsTrottle(UserRateThrottle):
    rate = '30/minute'

@throttle_classes([GetSortsAndDetailsTrottle])
@api_view(['POST'])
def get_sorts(request):
    try:
        data = request.data
        category = data.get("category", "").strip().lower()
        
        if category == "дерева":
            sorts = Sort_tree.objects.values_list("sort", flat=True)
        elif category == "овочі":
            sorts = Sort_veg.objects.values_list("Name", flat=True)
        elif category == "рослини":
            sorts = Plants.objects.values_list("name", flat=True)
        else:
            return JsonResponse({"error": "Невідома категорія"}, status=400)
        
        return JsonResponse(list(sorts), safe=False)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Некоректний JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



def calendar(request):
    return render(request, 'calendar.html')

@throttle_classes([GetSortsAndDetailsTrottle])
@api_view(['POST'])
def get_sort_details(request):
    try:
        data = request.data
        category = data.get("category", "").strip().lower()
        sort_name = data.get("sort_name", "").strip()
        
        if category == "дерева":
            sort = Sort_tree.objects.filter(sort=sort_name).first()
            if not sort:
                return JsonResponse({"error": "Сорт не знайдено"}, status=404)
                
            tree = sort.tree
            if not tree:
                return JsonResponse({"error": "Дерево не знайдено"}, status=404)

            values = {
                "Scope_of_bloom_From": tree.Scope_of_bloom_From,
                "Scope_of_bloom_To": tree.Scope_of_bloom_To,
                "Ripe_Time_From": tree.Ripe_Time_From,
                "Ripe_Time_To": tree.Ripe_Time_To,
            }

            if sort.Usage == "Садівництво":
                plantings = Planting.objects.filter(id__in=[1, 2])
                for i, planting in enumerate(plantings, start=1):
                    values.update({
                        f"Planting_time_From{i}": planting.Plant_time_From,
                        f"Planting_time_To{i}": planting.Plant_time_To
                    })

            # Додаємо всі періоди обрізки
            cuttings = Cutting.objects.all()
            for i, cutting in enumerate(cuttings, start=1):
                values.update({
                    f"Cutting_time_From{i}": cutting.Cutting_time_From,
                    f"Cutting_time_To{i}": cutting.Cutting_time_To
                })

            # Додаємо всі періоди удобрення
            fertilizers = Fertilizer.objects.all()
            for i, fertilizer in enumerate(fertilizers, start=1):
                values.update({
                    f"Fertilizer_date_From1_{i}": fertilizer.Fertilizer_date_From1,
                    f"Fertilizer_date_To1_{i}": fertilizer.Fertilizer_date_To1,
                    f"Fertilizer_date_From2_{i}": fertilizer.Fertilizer_date_From2,
                    f"Fertilizer_date_To2_{i}": fertilizer.Fertilizer_date_To2
                })

    
        
        elif category == "овочі":
            sort = Sort_veg.objects.filter(Name=sort_name).first()
            if sort:
                veg = sort.vegetables_idVeg
                if veg:
                    values = {
                    "Plant_time_From1": veg.Plant_time_From1,
                    "Plant_time_From2": veg.Plant_time_From2,
                    "Plant_time_To1": veg.Plant_time_To1,
                    "Plant_time_To2": veg.Plant_time_To2,
                    "Ripe_time_From1": sort.Ripe_time_From1,
                    "Ripe_time_To1":  sort.Ripe_time_To1,
                    "Ripe_time_From2": sort.Ripe_time_From2,
                    "Ripe_time_To2": sort.Ripe_time_To2,
                }
                    fertilizers = Fertilizer_veg.objects.all()
                    for i, fertilizer in enumerate(fertilizers, start=1):
                        values.update({
                            f"Fertilizer_date_From1_{i}": fertilizer.Time_Fertilizer_From1,
                            f"Fertilizer_date_To1_{i}": fertilizer.Time_Fertilizer_To1,
                            f"Fertilizer_date_From2_{i}": fertilizer.Time_Fertilizer_From2,
                            f"Fertilizer_date_To2_{i}": fertilizer.Time_Fertilizer_To2
                        })
                else:
                    return JsonResponse({"error": "Сорт не знайдено"}, status=404)
            else:
                return JsonResponse({"error": "Сорт не знайдено"}, status=404)

        
        elif category == "рослини":
            plant = Plants.objects.filter(name=sort_name).first()
            if plant:
                values = {
                    "start_date": plant.start_date,
                    "end_date": plant.end_date,
                }
            else:
                return JsonResponse({"error": "Сорт не знайдено"}, status=404)
        
        else:
            return JsonResponse({"error": "Невідома категорія"}, status=400)
        
        return JsonResponse(values)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Некоректний JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
