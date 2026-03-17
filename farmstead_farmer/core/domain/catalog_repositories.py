from abc import ABC, abstractmethod


class CatalogRepository(ABC):
    @abstractmethod
    def search(self, query: str) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def list_catalog_cards(self, categories: list[str]) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def list_animals(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def list_animal_sorts(self, animal_id: int) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_animal_detail(self, animal_id: int, sort_id: int) -> dict:
        raise NotImplementedError
