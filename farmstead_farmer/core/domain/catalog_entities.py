from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CatalogCard:
    category: str
    common_name: str
    image_url: str
    url: str

    def as_dict(self) -> dict:
        return {
            "category": self.category,
            "common_name": self.common_name,
            "image_url": self.image_url,
            "url": self.url,
        }


@dataclass(frozen=True)
class AnimalListItem:
    id: int
    name: str
    image: str

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "image": self.image,
        }


@dataclass(frozen=True)
class AnimalSortItem:
    id: int
    name: str
    image: str

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "image": self.image,
        }


@dataclass(frozen=True)
class AnimalDetail:
    id: int
    common_name: str
    scientific_name: str
    class_field: str
    genus: str
    family: str
    lifespan: str
    habitat: str
    diet: str
    image: str
    description: str

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "common_name": self.common_name,
            "scientific_name": self.scientific_name,
            "class_field": self.class_field,
            "genus": self.genus,
            "family": self.family,
            "lifespan": self.lifespan,
            "habitat": self.habitat,
            "diet": self.diet,
            "image": self.image,
            "description": self.description,
        }
