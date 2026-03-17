from core.domain.entities import FavoriteViewItem
from core.domain.exceptions import InvalidTokenError, MissingFieldError, UserNotFoundError
from core.domain.repositories import UserRepository


class ProfileUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def _to_favorite_view(self, item: dict) -> FavoriteViewItem:
        return FavoriteViewItem(
            common_name=item.get("name", "Невідомий обʼєкт"),
            image_url=item.get("image_url", "default.jpg"),
            url=item.get("link", "#"),
            category=item.get("category", "Без категорії"),
        )

    def toggle_map_private(self, token: str) -> dict:
        if not token:
            raise InvalidTokenError("Неправильний токен")

        user = self.user_repository.find_by_token(token)
        if user is None:
            raise InvalidTokenError("Неправильний токен")

        user.is_map_private = not bool(user.is_map_private)
        self.user_repository.save(user)
        value = 1 if user.is_map_private else 0
        return {"status": f"Статус змінено на {value}"}

    def toggle_favorite_private(self, token: str) -> dict:
        if not token:
            raise InvalidTokenError("Неправильний токен")

        user = self.user_repository.find_by_token(token)
        if user is None:
            raise InvalidTokenError("Невірний токен")

        user.is_favorite_private = not bool(user.is_favorite_private)
        self.user_repository.save(user)
        value = 1 if user.is_favorite_private else 0
        return {"status": f"Статус змінено на {value}"}

    def check_profile(self, token: str, username: str) -> dict:
        if not username:
            raise MissingFieldError("Username відсутній")

        if not token:
            return {"favorites": []}

        user_from_token = self.user_repository.find_by_token(token)
        if user_from_token is None:
            raise InvalidTokenError("Неправильний токен")

        if user_from_token.username != username:
            return {"favorites": []}

        user = self.user_repository.get_by_username(username)
        if user is None:
            raise UserNotFoundError("Користувача не знайдено")

        favorite_items = []
        if user_from_token == user and user.is_favorite_private:
            favorite_items = [self._to_favorite_view(item).as_dict() for item in (user.favorites or [])]

        return {"favorites": favorite_items}

    def check_map_visibility(self, token: str, username: str) -> dict:
        if not username:
            raise MissingFieldError("Username відсутній")

        profile_user = self.user_repository.get_by_username(username)
        if profile_user is None:
            raise UserNotFoundError("Користувача не знайдено")

        user_from_token = self.user_repository.find_by_token(token) if token else None
        if user_from_token is None:
            return {"show_map": bool(profile_user.has_map and not profile_user.is_map_private)}

        if user_from_token == profile_user and user_from_token.has_map:
            return {"show_map": True}

        return {"show_map": bool(profile_user.has_map and not profile_user.is_map_private)}
