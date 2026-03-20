from abc import ABC, abstractmethod
from typing import Any


class MapRepository(ABC):
    @abstractmethod
    def save_map(self, user_id: int, content: Any) -> int:
        raise NotImplementedError

    @abstractmethod
    def update_map(self, user_id: int, content: Any, map_id: int | None = None) -> int:
        raise NotImplementedError

    @abstractmethod
    def has_map(self, user_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_map(self, user_id: int, map_id: int | None = None) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_tree_sorts(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def get_vegetable_sorts(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def get_compatibility_index(self) -> dict:
        raise NotImplementedError
