from typing import Optional

from core.domain.forum_repositories import ForumRepository
from core.domain.repositories import UserRepository
from core.domain.exceptions import InvalidTokenError


class ForumUseCase:
    def __init__(self, forum_repo: ForumRepository, user_repo: UserRepository):
        self.forum = forum_repo
        self.users = user_repo

    # ------------------------------------------------------------------ topics

    def get_topics(self) -> list:
        return self.forum.get_all_topics()

    def get_popular_topics(self) -> list:
        return self.forum.get_topics_by_likes()

    def topic_detail(self, topic_id: int) -> Optional[dict]:
        return self.forum.get_topic_detail(topic_id)

    def create_topic(self, category, title, content, author, time, date,
                     likes, dislikes, comments) -> int:
        return self.forum.create_topic(
            category, title, content, author, time, date, likes, dislikes, comments,
        )

    def update_topic(self, topic_id: int, title: str, content: str, category: str) -> None:
        self.forum.update_topic(topic_id, title, content, category)

    def delete_topic(self, topic_id: int, topic_url: str) -> None:
        self.forum.delete_comments_for_topic(topic_id)
        self.users.remove_favorite_url_from_all(topic_url)
        self.forum.delete_topic(topic_id)

    def toggle_topic_reaction(self, topic_id: int, token: str, reaction: str) -> dict:
        user = self.users.find_by_token(token)
        if user is None:
            raise InvalidTokenError('Invalid token')
        return self.forum.toggle_topic_reaction(topic_id, user.id, reaction)

    def get_user_topic_reaction(self, topic_id: int, token: str) -> str:
        user = self.users.find_by_token(token)
        if user is None:
            raise InvalidTokenError('Invalid token')
        return self.forum.get_user_topic_reaction(topic_id, user.id)

    # ---------------------------------------------------------------- comments

    def get_comment(self, comment_id: int) -> Optional[dict]:
        return self.forum.get_comment(comment_id)

    def get_comments_for_topic(self, topic_id: int) -> list:
        return self.forum.get_comments_for_topic(topic_id)

    def create_comment(self, topic_id, content, author, date, time,
                       topics_id, receiver, is_answer, parent_id) -> dict:
        result = self.forum.create_comment(
            topic_id, content, author, date, time,
            topics_id, receiver, is_answer, parent_id,
        )
        
        if receiver and receiver != author:
            notif_link = f"/forum/topic/{topics_id}/#comment-{result['id']}"
            self.forum.create_notification(
                owner_username=receiver,
                content=f"{author} відповів на ваше повідомлення",
                link=notif_link
            )
        return result

    def update_comment(self, comment_id: int, content: str,
                       actor: Optional[str] = None) -> None:
        self.forum.update_comment_content(comment_id, content, actor)

    def delete_comment(self, comment_id: int, topic_id: int) -> None:
        self.forum.delete_comment(comment_id, topic_id)

    def toggle_comment_reaction(self, comment_id: int, token: str, reaction: str) -> dict:
        user = self.users.find_by_token(token)
        if user is None:
            raise InvalidTokenError('Invalid token')
        return self.forum.toggle_comment_reaction(comment_id, user.id, reaction)
    # ------------------------------------------------------------------ notifications
    def create_comment(self, topic_id, content, author, date, time,
                   topics_id, receiver, is_answer, parent_id) -> dict:
        # Створюємо коментар
        result = self.forum.create_comment(
            topic_id, content, author, date, time,
            topics_id, receiver, is_answer, parent_id,
        )
        
        # Створюємо сповіщення, якщо отримувач не є автором коментаря
        if receiver and receiver != author:
            short_content = content[:50] + "..." if len(content) > 50 else content
            notif_link = f"/forum/topic/{topics_id}/#comment-{result['id']}"
            self.forum.create_notification(
                owner_username=receiver,
                content=f"{author} відповів: {short_content}",
                link=notif_link
            )
        return result

    def fetch_notifications(self, token: str) -> list:
        user = self.users.find_by_token(token)
        if not user: raise InvalidTokenError()
        self.forum.delete_old_notifications() # Очистка старих
        return self.forum.get_notifications(user.username)

    def mark_notification_read(self, token: str, notification_id: int) -> bool:
        user = self.users.find_by_token(token)
        if not user: raise InvalidTokenError()
        return self.forum.mark_notification_as_read(notification_id, user.username)

    # ------------------------------------------------------------------ misc

    def update_author_name(self, old_name: str, new_name: str) -> None:
        self.forum.update_author_name(old_name, new_name)
