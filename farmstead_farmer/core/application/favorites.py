from core.domain.entities import FavoriteItem
from core.domain.exceptions import InvalidTokenError, MissingFieldError
from core.domain.repositories import UserRepository


class FavoriteUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def _build_item(self, payload: dict) -> FavoriteItem:
        required_fields = ["name", "link", "category"]
        if not all(field in payload for field in required_fields):
            raise MissingFieldError("Відсутні необхідні дані.")
        return FavoriteItem(
            name=payload["name"],
            image_url=payload.get("image_url"),
            link=payload["link"],
            category=payload["category"],
        )

    def toggle(self, token: str, payload: dict) -> dict:
        if not token:
            raise MissingFieldError("Токен не надано.")

        user = self.user_repository.find_by_token(token)
        if user is None:
            raise InvalidTokenError("Недійсний токен.")

        favorite_item = self._build_item(payload).as_dict()
        favorites = list(user.favorites or [])

        if favorite_item in favorites:
            favorites.remove(favorite_item)
            action = "removed"
        else:
            favorites.append(favorite_item)
            action = "added"

        user.favorites = favorites
        self.user_repository.save(user)
        return {"status": action, "favorites": favorites}

    def check(self, token: str, payload: dict) -> dict:
        if not token:
            raise MissingFieldError("Токен не надано.")

        user = self.user_repository.find_by_token(token)
        if user is None:
            raise InvalidTokenError("Недійсний токен.")

        favorite_item = self._build_item(payload).as_dict()
        status = "inside" if favorite_item in (user.favorites or []) else "not inside"
        return {"status": status}
