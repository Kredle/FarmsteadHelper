from core.domain.map_repositories import MapRepository


class MapUseCase:
    def __init__(self, repository: MapRepository):
        self.repository = repository

    def save_map(self, user_id: int, content, map_name: str | None = None) -> dict:
        map_id = self.repository.save_map(user_id, content, map_name=map_name)
        return {
            "status": "success",
            "message": "Map saved successfully",
            "map_id": map_id,
        }

    def update_map(self, user_id: int, content, map_id: int | None = None, map_name: str | None = None) -> dict:
        map_id = self.repository.update_map(user_id, content, map_id, map_name=map_name)
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

    def get_map(self, user_id: int, map_id: int | None = None) -> dict:
        return self.repository.get_map(user_id, map_id)

    def list_maps(self, user_id: int) -> list[dict]:
        return self.repository.list_maps(user_id)

    def update_map_settings(self, user_id: int, map_id: int, map_name: str | None = None, is_private: bool | None = None) -> dict:
        updated = self.repository.update_map_settings(user_id, map_id, map_name=map_name, is_private=is_private)
        return {
            'status': 'success',
            'map': updated,
        }

    def delete_map(self, user_id: int, map_id: int) -> dict:
        self.repository.delete_map(user_id, map_id)
        return {
            'status': 'success',
            'message': 'Map deleted successfully',
        }

    def tree_sorts(self) -> list[dict]:
        return self.repository.get_tree_sorts()

    def vegetable_sorts(self) -> list[dict]:
        return self.repository.get_vegetable_sorts()

    def compatibility_index(self) -> dict:
        return self.repository.get_compatibility_index()
