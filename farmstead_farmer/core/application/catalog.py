from core.domain.catalog_repositories import CatalogRepository


class CatalogUseCase:
    def __init__(self, repository: CatalogRepository):
        self.repository = repository

    def search(self, query: str) -> dict:
        return {"results": self.repository.search(query.strip().lower())}

    def filter_cards(self, categories: list[str]) -> dict:
        allowed = {"animals", "flowers", "vegetables", "trees"}
        selected = [cat for cat in categories if cat in allowed]
        return {"items": self.repository.list_catalog_cards(selected)}

    def random_cards(self) -> dict:
        return {"items": self.repository.list_catalog_cards(["animals", "flowers", "vegetables", "trees"])}

    def animals_list(self) -> list[dict]:
        return self.repository.list_animals()

    def animal_sorts(self, animal_id: int) -> dict:
        return self.repository.list_animal_sorts(animal_id)

    def animal_detail(self, animal_id: int, sort_id: int) -> dict:
        return self.repository.get_animal_detail(animal_id, sort_id)
