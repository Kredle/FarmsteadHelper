from core.domain.map_repositories import MapRepository


class MapUseCase:
    def __init__(self, repository: MapRepository):
        self.repository = repository

    def save_map(self, user_id: int, content) -> dict:
        map_id = self.repository.save_map(user_id, content)
        return {
            "status": "success",
            "message": "Map saved successfully",
            "map_id": map_id,
        }

    def update_map(self, user_id: int, content) -> dict:
        map_id = self.repository.update_map(user_id, content)
        return {
            "status": "success",
            "message": "Map saved successfully",
            "map_id": map_id,
        }

    def check_map(self, user_id: int) -> dict:
        return {
            "status": "success",
            "exists": self.repository.has_map(user_id),
        }

    def get_map(self, user_id: int) -> dict:
        return self.repository.get_map(user_id)

    def tree_sorts(self) -> list[dict]:
        return self.repository.get_tree_sorts()

    def vegetable_sorts(self) -> list[dict]:
        return self.repository.get_vegetable_sorts()
