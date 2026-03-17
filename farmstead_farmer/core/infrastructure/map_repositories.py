import json

from api.models import CustomUser
from core.domain.map_entities import MapSnapshot
from core.domain.map_repositories import MapRepository
from interactive_map.models import Map
from trees.models import Tree
from vegetables.models import Vegetables


class DjangoMapRepository(MapRepository):
    def _get_user(self, user_id: int) -> CustomUser:
        return CustomUser.objects.get(id=user_id)

    def save_map(self, user_id: int, content):
        author = self._get_user(user_id)
        author.has_map = True
        author.save()
        map_obj = Map(User_id=author, data=json.dumps(content))
        map_obj.save()
        return map_obj.id

    def update_map(self, user_id: int, content):
        author = self._get_user(user_id)
        author.has_map = True
        author.save()
        map_obj = Map.objects.get(User_id=author)
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
        tree_data = []
        for tree in Tree.objects.all():
            sorts_data = [{"id": sort.idSort, "sort": sort.sort} for sort in tree.sorts.all()]
            tree_data.append({"id": tree.idTree, "name": tree.name, "sorts": sorts_data})
        return tree_data

    def get_vegetable_sorts(self) -> list[dict]:
        vegetable_data = []
        for vegetable in Vegetables.objects.all():
            sorts_data = [{"idSort": sort.idSort, "Name": sort.Name} for sort in vegetable.sorts_veg.all()]
            vegetable_data.append({"idVeg": vegetable.idVeg, "Name": vegetable.Name, "sortsVeg": sorts_data})
        return vegetable_data
