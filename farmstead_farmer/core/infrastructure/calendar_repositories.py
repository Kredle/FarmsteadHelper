from typing import List

from calendar_.models import (
    Sort_tree, Sort_veg, Plants,
    Cutting, Planting, Fertilizer, Fertilizer_veg,
)
from core.domain.calendar_repositories import CalendarRepository
from core.domain.exceptions import DomainError


class CategoryNotFoundError(DomainError):
    pass


class SortNotFoundError(DomainError):
    pass


class DjangoCalendarRepository(CalendarRepository):

    def get_sorts(self, category: str) -> List[str]:
        if category == 'дерева':
            return list(Sort_tree.objects.values_list('sort', flat=True))
        if category == 'овочі':
            return list(Sort_veg.objects.values_list('Name', flat=True))
        if category == 'рослини':
            return list(Plants.objects.values_list('name', flat=True))
        raise CategoryNotFoundError(f'Unknown category: {category}')

    def get_sort_details(self, category: str, sort_name: str) -> dict:
        if category == 'дерева':
            return self._tree_details(sort_name)
        if category == 'овочі':
            return self._veg_details(sort_name)
        if category == 'рослини':
            return self._plant_details(sort_name)
        raise CategoryNotFoundError(f'Unknown category: {category}')

    # ---------------------------------------------------------------- private

    def _tree_details(self, sort_name: str) -> dict:
        sort = Sort_tree.objects.filter(sort=sort_name).first()
        if not sort:
            raise SortNotFoundError('Sort not found')
        tree = sort.tree
        if not tree:
            raise SortNotFoundError('Tree not found')

        values = {
            'Scope_of_bloom_From': tree.Scope_of_bloom_From,
            'Scope_of_bloom_To': tree.Scope_of_bloom_To,
            'Ripe_Time_From': tree.Ripe_Time_From,
            'Ripe_Time_To': tree.Ripe_Time_To,
        }

        if sort.Usage == 'Садівництво':
            for i, p in enumerate(Planting.objects.filter(id__in=[1, 2]), start=1):
                values[f'Planting_time_From{i}'] = p.Plant_time_From
                values[f'Planting_time_To{i}'] = p.Plant_time_To

        for i, c in enumerate(Cutting.objects.all(), start=1):
            values[f'Cutting_time_From{i}'] = c.Cutting_time_From
            values[f'Cutting_time_To{i}'] = c.Cutting_time_To

        for i, f in enumerate(Fertilizer.objects.all(), start=1):
            values[f'Fertilizer_date_From1_{i}'] = f.Fertilizer_date_From1
            values[f'Fertilizer_date_To1_{i}'] = f.Fertilizer_date_To1
            values[f'Fertilizer_date_From2_{i}'] = f.Fertilizer_date_From2
            values[f'Fertilizer_date_To2_{i}'] = f.Fertilizer_date_To2

        return values

    def _veg_details(self, sort_name: str) -> dict:
        sort = Sort_veg.objects.filter(Name=sort_name).first()
        if not sort:
            raise SortNotFoundError('Sort not found')
        veg = sort.vegetables_idVeg
        if not veg:
            raise SortNotFoundError('Vegetable not found')

        values = {
            'Plant_time_From1': veg.Plant_time_From1,
            'Plant_time_From2': veg.Plant_time_From2,
            'Plant_time_To1': veg.Plant_time_To1,
            'Plant_time_To2': veg.Plant_time_To2,
            'Ripe_time_From1': sort.Ripe_time_From1,
            'Ripe_time_To1': sort.Ripe_time_To1,
            'Ripe_time_From2': sort.Ripe_time_From2,
            'Ripe_time_To2': sort.Ripe_time_To2,
        }
        for i, f in enumerate(Fertilizer_veg.objects.all(), start=1):
            values[f'Fertilizer_date_From1_{i}'] = f.Time_Fertilizer_From1
            values[f'Fertilizer_date_To1_{i}'] = f.Time_Fertilizer_To1
            values[f'Fertilizer_date_From2_{i}'] = f.Time_Fertilizer_From2
            values[f'Fertilizer_date_To2_{i}'] = f.Time_Fertilizer_To2

        return values

    def _plant_details(self, sort_name: str) -> dict:
        plant = Plants.objects.filter(name=sort_name).first()
        if not plant:
            raise SortNotFoundError('Plant not found')
        return {
            'start_date': plant.start_date,
            'end_date': plant.end_date,
        }
