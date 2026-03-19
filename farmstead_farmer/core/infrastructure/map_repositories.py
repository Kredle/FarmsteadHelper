import json
import re
from typing import Any

from api.models import CustomUser
from core.domain.map_entities import MapSnapshot
from core.domain.map_repositories import MapRepository
from django.db import connection
from interactive_map.models import Map

from core.infrastructure.incompatibility_parser import IncompatibilityParserUA
from core.infrastructure.soil_parser import SoilTypeParserUA


ALLOWED_ENTITY_TERRAINS = {'grass', 'dirt', 'mud'}


TREE_DEFAULT_RADIUS = 140
VEGETABLE_DEFAULT_RADIUS = 90
BASE_SPECIES_OVERRIDES = {
    'яблуня': ['груша'],
    'груша': ['яблуня'],
}


def _slugify_species_id(name: str) -> str:
    value = str(name or '').strip().lower()
    value = re.sub(r'\s+', '_', value)
    value = re.sub(r'[^a-zа-щьюяґєії0-9_\-]', '', value)
    return value


def _base_species_id(name: str) -> str:
    normalized = str(name or '').strip().lower()
    if not normalized:
        return ''
    head = normalized.split()[0]
    return _slugify_species_id(head)


def _guess_tree_categories(name: str) -> list[str]:
    n = str(name or '').lower()
    categories = ['tree']

    if any(token in n for token in ('слив', 'персик', 'абрикос', 'вишн', 'черешн')):
        categories.append('кісточкові')
    if any(token in n for token in ('яблун', 'груш')):
        categories.append('зерняткові')

    return sorted(set(categories))


def _guess_vegetable_categories(name: str) -> list[str]:
    n = str(name or '').lower()
    categories = ['vegetable']

    if any(token in n for token in ('гарбуз', 'огір', 'кабач', 'дин', 'кавун')):
        categories.append('гарбузові')
    if any(token in n for token in ('помідор', 'перець', 'баклаж')):
        categories.append('пасльонові')
    if any(token in n for token in ('моркв', 'петруш', 'селера', 'кріп')):
        categories.append('зонтичні')

    return sorted(set(categories))


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

    def _fetch_known_species_names(self) -> list[str]:
        with connection.cursor() as cursor:
            cursor.execute('SELECT "Name" FROM tree WHERE "Name" IS NOT NULL')
            tree_names = [str(row[0]).strip().lower() for row in cursor.fetchall() if row and row[0]]

            cursor.execute('SELECT "Name" FROM vegetables WHERE "Name" IS NOT NULL')
            vegetable_names = [str(row[0]).strip().lower() for row in cursor.fetchall() if row and row[0]]

        return list({*tree_names, *vegetable_names})

    def _build_soil_index(self) -> dict:
        parser = SoilTypeParserUA()
        unique_soils: set[str] = set()

        tree_sort_soils: dict[str, list[str]] = {}
        vegetable_sort_soils: dict[str, list[str]] = {}

        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT idsort, ground_type
                FROM sorts
                '''
            )
            tree_rows = cursor.fetchall()

            cursor.execute(
                '''
                SELECT "idSort", "Name"
                FROM sorts_veg
                '''
            )
            vegetable_rows = cursor.fetchall()

        for sort_id, raw_ground in tree_rows:
            soils = parser.parse(str(raw_ground or ''))
            tree_sort_soils[str(sort_id)] = soils
            unique_soils.update(soils)

        # Vegetables table in current schema does not contain dedicated ground_type.
        # Keep explicit empty lists for predictable API contract.
        for veg_sort_id, _veg_sort_name in vegetable_rows:
            vegetable_sort_soils[str(veg_sort_id)] = []

        return {
            'soil_types': sorted(unique_soils),
            'tree_sort_soils': tree_sort_soils,
            'vegetable_sort_soils': vegetable_sort_soils,
        }

    def _build_compatibility_index(self) -> dict:
        known_species = self._fetch_known_species_names()
        parser = IncompatibilityParserUA(known_species)
        soil_index = self._build_soil_index()

        trees: dict[str, dict] = {}
        vegetables: dict[str, dict] = {}

        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT idtree, "Name", incompatible
                FROM tree
                '''
            )
            tree_rows = cursor.fetchall()

            cursor.execute(
                '''
                SELECT "idVeg", "Name", "Incompatible"
                FROM vegetables
                '''
            )
            vegetable_rows = cursor.fetchall()

        for tree_id, tree_name, raw_incompatible in tree_rows:
            parsed = parser.parse(str(raw_incompatible or ''))
            species_name = str(tree_name or '').strip().lower()
            base_species = _base_species_id(species_name)
            incompatible_ids = [_slugify_species_id(item) for item in parsed.incompatible_species_names]
            incompatible_ids.extend(BASE_SPECIES_OVERRIDES.get(base_species, []))
            trees[str(tree_id)] = {
                'species_name': species_name,
                'species_id': _slugify_species_id(species_name),
                'base_species_id': base_species,
                'category_ids': _guess_tree_categories(species_name),
                'radius': TREE_DEFAULT_RADIUS,
                'incompatible_species_names': parsed.incompatible_species_names,
                'incompatible_species_ids': sorted(set(filter(None, incompatible_ids))),
                'incompatible_categories': parsed.incompatible_categories,
            }

        for vegetable_id, vegetable_name, raw_incompatible in vegetable_rows:
            parsed = parser.parse(str(raw_incompatible or ''))
            species_name = str(vegetable_name or '').strip().lower()
            base_species = _base_species_id(species_name)
            incompatible_ids = [_slugify_species_id(item) for item in parsed.incompatible_species_names]
            incompatible_ids.extend(BASE_SPECIES_OVERRIDES.get(base_species, []))
            vegetables[str(vegetable_id)] = {
                'species_name': species_name,
                'species_id': _slugify_species_id(species_name),
                'base_species_id': base_species,
                'category_ids': _guess_vegetable_categories(species_name),
                'radius': VEGETABLE_DEFAULT_RADIUS,
                'incompatible_species_names': parsed.incompatible_species_names,
                'incompatible_species_ids': sorted(set(filter(None, incompatible_ids))),
                'incompatible_categories': parsed.incompatible_categories,
            }

        return {
            'trees': trees,
            'vegetables': vegetables,
            'soil_types': soil_index.get('soil_types', []),
        }

    def get_compatibility_index(self) -> dict:
        return self._build_compatibility_index()

    def get_tree_sorts(self) -> list[dict]:
        compatibility_index = self._build_compatibility_index()
        tree_compatibility = compatibility_index.get('trees', {})
        soil_index = self._build_soil_index()
        tree_sort_soils = soil_index.get('tree_sort_soils', {})

        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT
                    t.idtree,
                    t."Name",
                    s.idsort,
                    s.sort,
                    s.ground_type
                FROM tree t
                LEFT JOIN sorts s ON s.tree_idtree = t.idtree
                ORDER BY t."Name", s.sort
                '''
            )
            rows = cursor.fetchall()

        trees_by_id: dict[int, dict] = {}
        for tree_id, tree_name, sort_id, sort_name, sort_ground_type in rows:
            if tree_id not in trees_by_id:
                compatibility = tree_compatibility.get(str(tree_id), {})
                trees_by_id[tree_id] = {
                    "id": tree_id,
                    "name": tree_name,
                    "species_id": compatibility.get('species_id', _slugify_species_id(tree_name)),
                    "base_species_id": compatibility.get('base_species_id', _base_species_id(tree_name)),
                    "category_ids": compatibility.get('category_ids', ['tree']),
                    "radius": compatibility.get('radius', TREE_DEFAULT_RADIUS),
                    "incompatible_species_ids": compatibility.get('incompatible_species_ids', []),
                    "incompatible_categories": compatibility.get('incompatible_categories', []),
                    "sorts": [],
                }
            if sort_id is not None:
                trees_by_id[tree_id]["sorts"].append(
                    {
                        "id": sort_id,
                        "sort": sort_name,
                        "ground_type_raw": sort_ground_type,
                        "allowed_soils": tree_sort_soils.get(str(sort_id), []),
                    }
                )

        return list(trees_by_id.values())

    def get_vegetable_sorts(self) -> list[dict]:
        compatibility_index = self._build_compatibility_index()
        vegetable_compatibility = compatibility_index.get('vegetables', {})
        soil_index = self._build_soil_index()
        vegetable_sort_soils = soil_index.get('vegetable_sort_soils', {})

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
                compatibility = vegetable_compatibility.get(str(vegetable_id), {})
                vegetables_by_id[vegetable_id] = {
                    "idVeg": vegetable_id,
                    "Name": vegetable_name,
                    "species_id": compatibility.get('species_id', _slugify_species_id(vegetable_name)),
                    "base_species_id": compatibility.get('base_species_id', _base_species_id(vegetable_name)),
                    "category_ids": compatibility.get('category_ids', ['vegetable']),
                    "radius": compatibility.get('radius', VEGETABLE_DEFAULT_RADIUS),
                    "incompatible_species_ids": compatibility.get('incompatible_species_ids', []),
                    "incompatible_categories": compatibility.get('incompatible_categories', []),
                    "sortsVeg": [],
                }
            if sort_id is not None:
                vegetables_by_id[vegetable_id]["sortsVeg"].append(
                    {
                        "idSort": sort_id,
                        "Name": sort_name,
                        "allowed_soils": vegetable_sort_soils.get(str(sort_id), []),
                    }
                )

        return list(vegetables_by_id.values())
