import random

from django.db.models import Q
from django.shortcuts import get_object_or_404

from animals.models import Animal_main, Animal as AnimalModel
from catalog.models import Animal, Plant, FindVeg_sort, FindTree_sort, FindTree, FindVeg, Tree, Vegetable
from core.domain.catalog_entities import AnimalDetail, AnimalListItem, AnimalSortItem, CatalogCard
from core.domain.catalog_repositories import CatalogRepository


class DjangoCatalogRepository(CatalogRepository):
    def search(self, query: str) -> list[dict]:
        if not query:
            return []

        trees = FindTree.objects.filter(Q(common_name2__icontains=query))
        flowers = Plant.objects.filter(Q(common_name__icontains=query))
        animals = Animal.objects.filter(Q(common_name__icontains=query))
        vegetables = FindVeg.objects.filter(Q(common_name2__icontains=query))
        tree_sorts = FindTree_sort.objects.filter(Q(common_name__icontains=query))
        veg_sorts = FindVeg_sort.objects.filter(Q(common_name__icontains=query))

        results = []
        for tree in trees:
            results.append({
                "type": "Дерево",
                "name": tree.common_name2,
                "image_url": tree.image_url or "",
                "url": f"/catalog/trees/{tree.idTree}",
            })
        for flower in flowers:
            results.append({
                "type": "Квітка",
                "name": flower.common_name,
                "image_url": flower.image_url or "",
                "url": f"/catalog/flowers/{flower.sort_id}",
            })
        for animal in animals:
            results.append({
                "type": "Тварина",
                "name": animal.common_name,
                "image_url": animal.image_url or "",
                "url": f"/catalog/animals/{animal.sort_id}",
            })
        for vegetable in vegetables:
            results.append({
                "type": "Овоч",
                "name": vegetable.common_name2,
                "image_url": vegetable.image_url or "",
                "url": f"/catalog/vegetables/{vegetable.idVeg}",
            })
        for veg_sort in veg_sorts:
            results.append({
                "type": "Овоч",
                "name": veg_sort.common_name,
                "image_url": veg_sort.image_url or "",
                "url": f"/catalog/vegetables/{veg_sort.idVeg}/{veg_sort.idVeg_sort}",
            })
        for tree_sort in tree_sorts:
            results.append({
                "type": "Дерево",
                "name": tree_sort.common_name,
                "image_url": tree_sort.image_url or "",
                "url": f"/catalog/trees/{tree_sort.idTree}/{tree_sort.idTree_sort}",
            })

        return results

    def list_catalog_cards(self, categories: list[str]) -> list[dict]:
        all_items = []
        if "animals" in categories:
            all_items.extend(Animal.objects.all())
        if "flowers" in categories:
            all_items.extend(Plant.objects.all())
        if "vegetables" in categories:
            all_items.extend(Vegetable.objects.filter(vegetable__isnull=False))
        if "trees" in categories:
            all_items.extend(Tree.objects.filter(tree__isnull=False))

        random.shuffle(all_items)
        cards = []
        for item in all_items[:9]:
            if isinstance(item, Animal):
                cards.append(CatalogCard("animals", item.common_name, item.image_url or "", f"/catalog/animals/{item.sort_id}").as_dict())
            elif isinstance(item, Plant):
                cards.append(CatalogCard("flowers", item.common_name, item.image_url or "", f"/catalog/flowers/{item.sort_id}").as_dict())
            elif isinstance(item, Vegetable) and item.vegetable:
                cards.append(CatalogCard("vegetables", item.common_name, item.image_url or "", f"/catalog/vegetables/{item.vegetable.id}/{item.sort_id}").as_dict())
            elif isinstance(item, Tree) and item.tree:
                cards.append(CatalogCard("trees", item.common_name, item.image_url or "", f"/catalog/trees/{item.tree.id}/{item.sort_id}").as_dict())
        return cards

    def list_animals(self) -> list[dict]:
        animals = Animal_main.objects.all()
        return [AnimalListItem(a.idAni, a.Name, a.Image).as_dict() for a in animals]

    def list_animal_sorts(self, animal_id: int) -> dict:
        animal = get_object_or_404(Animal_main, idAni=animal_id)
        sorts = [AnimalSortItem(s.id, s.common_name, s.image).as_dict() for s in animal.sorts.all()]
        return {
            "animal": {
                "id": animal.idAni,
                "name": animal.Name,
                "image": animal.Image,
            },
            "sorts": sorts,
        }

    def get_animal_detail(self, animal_id: int, sort_id: int) -> dict:
        sort = get_object_or_404(AnimalModel, id=sort_id, animal_idAni__idAni=animal_id)
        detail = AnimalDetail(
            id=sort.id,
            common_name=sort.common_name,
            scientific_name=sort.scientific_name,
            class_field=sort.class_field,
            genus=sort.genus,
            family=sort.family,
            lifespan=sort.lifespan,
            habitat=sort.habitat,
            diet=sort.diet,
            image=sort.image,
            description=sort.description,
        )
        return detail.as_dict()
