import json
from typing import Any

from api.models import CustomUser
from core.domain.map_entities import MapSnapshot
from core.domain.map_repositories import MapRepository
from django.db import connection
from interactive_map.models import Map


ALLOWED_ENTITY_TERRAINS = {'grass', 'dirt', 'mud'}


def _is_point_on_segment(px: float, py: float, ax: float, ay: float, bx: float, by: float) -> bool:
    epsilon = 1e-9
    cross = (py - ay) * (bx - ax) - (px - ax) * (by - ay)
    if abs(cross) > epsilon:
        return False

    dot = (px - ax) * (px - bx) + (py - ay) * (py - by)
    return dot <= epsilon


def _point_in_polygon(px: float, py: float, polygon: list[dict[str, Any]]) -> bool:
    if len(polygon) < 3:
        return False

    inside = False
    j = len(polygon) - 1

    for i in range(len(polygon)):
        xi = float(polygon[i].get('x', 0))
        yi = float(polygon[i].get('y', 0))
        xj = float(polygon[j].get('x', 0))
        yj = float(polygon[j].get('y', 0))

        if _is_point_on_segment(px, py, xi, yi, xj, yj):
            return True

        if (yi > py) != (yj > py):
            x_intersection = ((xj - xi) * (py - yi)) / (yj - yi) + xi
            if px < x_intersection:
                inside = not inside

        j = i

    return inside


def _terrain_at_point(x: float, y: float, figures: list[dict[str, Any]]) -> str | None:
    for figure in reversed(figures):
        fill_type = figure.get('fillType')
        points = figure.get('points')

        if not fill_type or not isinstance(points, list):
            continue

        if _point_in_polygon(x, y, points):
            return str(fill_type).lower()

    return None


def _validate_entity_placement(content: Any) -> None:
    if not isinstance(content, dict):
        return

    figures = content.get('figures') or []
    if not isinstance(figures, list):
        raise ValueError('Invalid map data: figures must be a list.')

    entity_groups = ('flowers', 'buildings', 'trees', 'vegetables')
    for group_name in entity_groups:
        entities = content.get(group_name) or []
        if not isinstance(entities, list):
            raise ValueError(f'Invalid map data: {group_name} must be a list.')

        for index, entity in enumerate(entities):
            if not isinstance(entity, dict):
                raise ValueError(f'Invalid entity in {group_name}[{index}].')

            x = entity.get('x')
            y = entity.get('y')
            if x is None or y is None:
                raise ValueError(f'Invalid entity coordinates in {group_name}[{index}].')

            try:
                x = float(x)
                y = float(y)
            except (TypeError, ValueError) as error:
                raise ValueError(f'Invalid entity coordinates in {group_name}[{index}].') from error

            terrain = _terrain_at_point(x, y, figures)
            if terrain not in ALLOWED_ENTITY_TERRAINS:
                raise ValueError(
                    'Entity placement is allowed only on grass or dirt terrain and is forbidden on water or void areas.'
                )


class DjangoMapRepository(MapRepository):
    def _get_user(self, user_id: int) -> CustomUser:
        return CustomUser.objects.get(id=user_id)

    def _next_map_id(self) -> int:
        last_map = Map.objects.order_by('-id').first()
        return 1 if last_map is None else int(last_map.id) + 1

    def save_map(self, user_id: int, content):
        _validate_entity_placement(content)
        author = self._get_user(user_id)
        author.has_map = True
        author.save()
        map_obj = Map.objects.filter(User_id=author).first()
        if map_obj is None:
            map_obj = Map(id=self._next_map_id(), User_id=author, data=json.dumps(content))
        else:
            map_obj.data = json.dumps(content)
        map_obj.save()
        return map_obj.id

    def update_map(self, user_id: int, content):
        _validate_entity_placement(content)
        author = self._get_user(user_id)
        author.has_map = True
        author.save()
        map_obj = Map.objects.filter(User_id=author).first()
        if map_obj is None:
            map_obj = Map(id=self._next_map_id(), User_id=author, data=json.dumps(content))
        else:
            map_obj.data = json.dumps(content)
        map_obj.save()
        return map_obj.id

    def has_map(self, user_id: int) -> bool:
        author = self._get_user(user_id)
        return Map.objects.filter(User_id=author).exists()

    def get_map(self, user_id: int) -> dict:
        author = self._get_user(user_id)
        map_obj = Map.objects.filter(User_id=author).first()
        if map_obj is None:
            return MapSnapshot(exists=False, owner_id=author.id, map_data=None).as_dict()
        return MapSnapshot(exists=True, owner_id=author.id, map_data=map_obj.data).as_dict()

    def get_tree_sorts(self) -> list[dict]:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT
                    t.idtree,
                    t."Name",
                    s.idsort,
                    s.sort
                FROM tree t
                LEFT JOIN sorts s ON s.tree_idtree = t.idtree
                ORDER BY t."Name", s.sort
                '''
            )
            rows = cursor.fetchall()

        trees_by_id: dict[int, dict] = {}
        for tree_id, tree_name, sort_id, sort_name in rows:
            if tree_id not in trees_by_id:
                trees_by_id[tree_id] = {
                    "id": tree_id,
                    "name": tree_name,
                    "sorts": [],
                }
            if sort_id is not None:
                trees_by_id[tree_id]["sorts"].append(
                    {
                        "id": sort_id,
                        "sort": sort_name,
                    }
                )

        return list(trees_by_id.values())

    def get_vegetable_sorts(self) -> list[dict]:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT
                    v."idVeg",
                    v."Name",
                    s."idSort",
                    s."Name"
                FROM vegetables v
                LEFT JOIN sorts_veg s ON s."vegetables_idVeg" = v."idVeg"
                ORDER BY v."Name", s."Name"
                '''
            )
            rows = cursor.fetchall()

        vegetables_by_id: dict[int, dict] = {}
        for vegetable_id, vegetable_name, sort_id, sort_name in rows:
            if vegetable_id not in vegetables_by_id:
                vegetables_by_id[vegetable_id] = {
                    "idVeg": vegetable_id,
                    "Name": vegetable_name,
                    "sortsVeg": [],
                }
            if sort_id is not None:
                vegetables_by_id[vegetable_id]["sortsVeg"].append(
                    {
                        "idSort": sort_id,
                        "Name": sort_name,
                    }
                )

        return list(vegetables_by_id.values())
