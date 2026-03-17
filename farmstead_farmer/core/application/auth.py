from datetime import timedelta

from django.contrib.auth.hashers import make_password
from django.utils import timezone

from core.domain.repositories import UserRepository
from core.domain.exceptions import InvalidTokenError, UserNotFoundError


class AuthUseCase:
    def __init__(self, user_repo: UserRepository):
        self.users = user_repo

    def issue_token(self, user) -> str:
        return self.users.get_or_create_token(user)

    def check_email_available(self, email: str) -> None:
        """Raises ValueError if the email is already taken."""
        if self.users.email_exists(email):
            raise ValueError('Email is already in use')

    def check_user_email_exists(self, email: str) -> bool:
        return self.users.find_by_email(email) is not None

    def reset_password(self, email: str, new_password: str, confirm_password: str) -> None:
        if not email or not new_password or not confirm_password:
            raise ValueError('All fields are required')
        if len(new_password) < 8:
            raise ValueError('Password must be at least 8 characters')
        if new_password != confirm_password:
            raise ValueError('Passwords do not match')
        user = self.users.find_by_email(email)
        if not user:
            raise UserNotFoundError('No user with this email')
        user.password = make_password(new_password)
        self.users.save(user)

    def change_username(self, token: str, new_username: str) -> None:
        if not token or not new_username:
            raise ValueError('Token and username are required')
        user = self.users.find_by_token(token)
        if not user:
            raise InvalidTokenError('Invalid token')
        if self.users.username_exists(new_username):
            raise ValueError('Username already taken')
        if user.last_username_update and \
                timezone.now() - user.last_username_update < timedelta(days=7):
            raise ValueError('Username can only be changed once every 7 days')
        user.username = new_username
        user.last_username_update = timezone.now()
        self.users.save(user)

    def change_bio(self, token: str, new_bio: str) -> None:
        if not token:
            raise ValueError('Token is required')
        user = self.users.find_by_token(token)
        if not user:
            raise InvalidTokenError('Invalid token')
        if len(new_bio) > 150:
            raise ValueError('Max 150 characters')
        user.bio = new_bio
        self.users.save(user)

    def change_password(self, token: str, current_password: str,
                        new_password: str, confirm_password: str) -> None:
        if not all([token, current_password, new_password, confirm_password]):
            raise ValueError('All fields are required')
        if new_password != confirm_password:
            raise ValueError('Passwords do not match')
        user = self.users.find_by_token(token)
        if not user:
            raise InvalidTokenError('Invalid token')
        if not user.check_password(current_password):
            raise ValueError('Incorrect current password')
        user.password = make_password(new_password)
        self.users.save(user)

    def get_profile_by_token(self, token_key: str) -> dict:
        """Returns full profile data dict and updates last_activity."""
        user = self.users.find_by_token(token_key)
        if not user:
            raise InvalidTokenError('Invalid token')
        self.users.update_last_activity(user)
        avatar_url = user.get_avatar_url()
        return {
            'username': user.username,
            'email': user.email,
            'firstname': user.firstname,
            'lastname': user.lastname,
            'bio': user.bio,
            'favorites': user.favorites,
            'avatarUrl': avatar_url,
            'lastActivity': user.last_activity,
            'dateJoined': user.date_joined,
            'flag': user.is_favorite_private,
            'id': user.id,
            'is_superuser': user.is_superuser,
            'map_flag': user.is_map_private,
        }

    def update_avatar(self, token: str, avatar_url: str) -> None:
        user = self.users.find_by_token(token)
        if not user:
            raise InvalidTokenError('Invalid token')
        user.avatar = avatar_url
        self.users.save(user)

    def update_name(self, token_key: str, firstname: str, lastname: str) -> tuple:
        """Returns (firstname, lastname) after saving."""
        user = self.users.find_by_token(token_key)
        if not user:
            raise InvalidTokenError('Invalid token')
        user.firstname = firstname
        user.lastname = lastname
        user.save(update_fields=['firstname', 'lastname'])
        return user.firstname, user.lastname

    def change_email(self, token: str, new_email: str) -> None:
        user = self.users.find_by_token(token)
        if not user:
            raise InvalidTokenError('Invalid token')
        if self.users.email_exists(new_email):
            raise ValueError('Email already registered')
        user.email = new_email
        self.users.save(user)

    def delete_account(self, email: str, password: str) -> None:
        user = self.users.find_by_email(email)
        if not user:
            raise UserNotFoundError('No user with this email')
        if not user.check_password(password):
            raise ValueError('Incorrect password')
        try:
            user.auth_token.delete()
        except Exception:
            pass
        self.users.delete(user)

    def toggle_superuser(self, username: str) -> bool:
        user = self.users.get_by_username(username)
        if not user:
            raise UserNotFoundError('User not found')
        user.is_superuser = not bool(user.is_superuser)
        self.users.save(user)
        return bool(user.is_superuser)

    def logout(self, token_key: str) -> None:
        self.users.delete_token(token_key)  # raises InvalidTokenError if missing
