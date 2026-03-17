from abc import ABC, abstractmethod
from typing import List


class UserRepository(ABC):
    @abstractmethod
    def get_by_token(self, token: str):
        raise NotImplementedError

    @abstractmethod
    def find_by_token(self, token: str):
        raise NotImplementedError

    @abstractmethod
    def get_by_username(self, username: str):
        raise NotImplementedError

    @abstractmethod
    def find_by_email(self, email: str):
        raise NotImplementedError

    @abstractmethod
    def save(self, user) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, user) -> None:
        raise NotImplementedError

    @abstractmethod
    def token_exists(self, token: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def email_exists(self, email: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def username_exists(self, username: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_staff_emails(self) -> List[str]:
        raise NotImplementedError

    @abstractmethod
    def get_superuser_emails(self) -> List[str]:
        raise NotImplementedError

    @abstractmethod
    def delete_token(self, token_key: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_or_create_token(self, user) -> str:
        raise NotImplementedError

    @abstractmethod
    def remove_favorite_url_from_all(self, url: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_last_activity(self, user) -> None:
        raise NotImplementedError
