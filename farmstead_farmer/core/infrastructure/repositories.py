from rest_framework.authtoken.models import Token
from django.utils import timezone
from typing import List

from api.models import CustomUser
from core.domain.repositories import UserRepository
from core.domain.exceptions import InvalidTokenError


class DjangoUserRepository(UserRepository):
    def get_by_token(self, token: str):
        return Token.objects.get(key=token).user

    def find_by_token(self, token: str):
        if not token:
            return None
        try:
            return self.get_by_token(token)
        except Token.DoesNotExist:
            return None

    def get_by_username(self, username: str):
        try:
            return CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return None

    def save(self, user) -> None:
        user.save()

    def delete(self, user) -> None:
        user.delete()

    def token_exists(self, token: str) -> bool:
        return Token.objects.filter(key=token).exists()

    def find_by_email(self, email: str):
        return CustomUser.objects.filter(email=email).first()

    def email_exists(self, email: str) -> bool:
        return CustomUser.objects.filter(email=email).exists()

    def username_exists(self, username: str) -> bool:
        return CustomUser.objects.filter(username=username).exists()

    def get_staff_emails(self) -> List[str]:
        return list(CustomUser.objects.filter(is_staff=True).values_list('email', flat=True))

    def delete_token(self, token_key: str) -> None:
        try:
            Token.objects.get(key=token_key).delete()
        except Token.DoesNotExist:
            raise InvalidTokenError('Token not found')

    def get_or_create_token(self, user) -> str:
        token, _ = Token.objects.get_or_create(user=user)
        return token.key

    def remove_favorite_url_from_all(self, url: str) -> None:
        for user in CustomUser.objects.all():
            original = len(user.favorites)
            user.favorites = [f for f in user.favorites if f.get('link') != url]
            if len(user.favorites) != original:
                user.save()

    def update_last_activity(self, user) -> None:
        user.last_activity = timezone.now()
        user.save(update_fields=['last_activity'])

    def get_superuser_emails(self) -> List[str]:
        return list(CustomUser.objects.filter(is_superuser=True).values_list('email', flat=True))
