from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class MapSnapshot:
    exists: bool
    owner_id: int
    map_id: Optional[int]
    map_data: Optional[Any]

    def as_dict(self) -> dict:
        return {
            "exists": self.exists,
            "owner_id": self.owner_id,
            "map_id": self.map_id,
            "map_data": self.map_data,
        }
