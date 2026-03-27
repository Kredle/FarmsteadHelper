import random

from django.db import connection
from django.db.models import Q
from django.shortcuts import get_object_or_404

from animals.models import Animal_main, Animal as AnimalModel
from catalog.models import Animal, Plant, FindVeg_sort, FindVeg, Vegetable, FindTree, FindTree_sort
from core.domain.catalog_entities import AnimalDetail, AnimalListItem, AnimalSortItem, CatalogCard
from core.domain.catalog_repositories import CatalogRepository


class DjangoCatalogRepository(CatalogRepository):
    def search(self, query: str) -> list[dict]:
        if not query:
            return []

        flowers = Plant.objects.filter(Q(common_name__icontains=query))
        animals = Animal.objects.filter(Q(common_name__icontains=query))
        vegetables = FindVeg.objects.filter(Q(common_name2__icontains=query))
        veg_sorts = FindVeg_sort.objects.filter(Q(common_name__icontains=query))
        trees = FindTree.objects.filter(Q(common_name2__icontains=query))
        tree_sorts = FindTree_sort.objects.filter(Q(common_name__icontains=query))

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
            animal_id = getattr(animal, 'animal_id', None)
            sort_id = getattr(animal, 'sort_id', None)
            if animal_id is None or sort_id is None:
                continue
            results.append({
                "type": "Тварина",
                "name": animal.common_name,
                "image_url": animal.image_url or "",
                "url": f"/catalog/animals/{animal_id}/{sort_id}",
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
        for sort in tree_sorts:
            results.append({
                "type": "Дерево",
                "name": sort.common_name,
                "image_url": sort.image_url or "",
                "url": f"/catalog/trees/{sort.idTree}/{sort.idTree_sort}",
            })

        return results

    def list_catalog_cards(self, categories: list[str]) -> list[dict]:
        cards = []

        if "animals" in categories:
            for item in Animal.objects.all():
                animal_id = getattr(item, 'animal_id', None)
                sort_id = getattr(item, 'sort_id', None)
                if animal_id is None or sort_id is None:
                    continue
                cards.append(
                    CatalogCard(
                        "animals",
                        item.common_name,
                        item.image_url or "",
                        f"/catalog/animals/{animal_id}/{sort_id}",
                    ).as_dict()
                )

        if "flowers" in categories:
            for item in Plant.objects.all():
                cards.append(
                    CatalogCard(
                        "flowers",
                        item.common_name,
                        item.image_url or "",
                        f"/catalog/flowers/{item.sort_id}",
                    ).as_dict()
                )

        if "vegetables" in categories:
            for item in Vegetable.objects.exclude(vegetable_id__isnull=True):
                veg_id = getattr(item, 'vegetable_id', None)
                sort_id = getattr(item, 'sort_id', None)
                if veg_id is None or sort_id is None:
                    continue
                cards.append(
                    CatalogCard(
                        "vegetables",
                        item.common_name,
                        item.image_url or "",
                        f"/catalog/vegetables/{veg_id}/{sort_id}",
                    ).as_dict()
                )

        if "trees" in categories:
            # Додаємо самі дерева (види)
            for item in FindTree.objects.all():
                cards.append(
                    CatalogCard(
                        "trees",
                        item.common_name2,
                        item.image_url or "",
                        f"/catalog/trees/{item.idTree}/",
                    ).as_dict()
                )
            # Додаємо сорти дерев (виключаючи ті, що не прив'язані до дерева)
            for item in FindTree_sort.objects.exclude(idTree__isnull=True):
                cards.append(
                    CatalogCard(
                        "trees",
                        item.common_name,
                        item.image_url or "",
                        f"/catalog/trees/{item.idTree}/{item.idTree_sort}",
                    ).as_dict()
                )

        random.shuffle(cards)
        return cards[:9]

    def list_animals(self) -> list[dict]:
        animals = Animal_main.objects.all()
        return [AnimalListItem(a.idAni, a.Name, a.Image).as_dict() for a in animals]

    def list_animal_sorts(self, animal_id: int) -> dict:
        animal = get_object_or_404(Animal_main, idAni=animal_id)
        print(f"sorts",animal.sorts.all())
        sorts = [AnimalSortItem(s.id, s.common_name, s.image).as_dict() for s in animal.sorts.all()]
        print(f"sorts", sorts)
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
