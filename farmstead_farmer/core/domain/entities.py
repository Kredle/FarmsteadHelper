from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class FavoriteItem:
    name: str
    link: str
    category: str
    image_url: Optional[str] = None

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "image_url": self.image_url,
            "link": self.link,
            "category": self.category,
        }


@dataclass(frozen=True)
class FavoriteViewItem:
    common_name: str
    image_url: str
    url: str
    category: str

    def as_dict(self) -> dict:
        return {
            "common_name": self.common_name,
            "image_url": self.image_url,
            "url": self.url,
            "category": self.category,
        }
