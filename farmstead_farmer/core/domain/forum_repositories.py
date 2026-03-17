from abc import ABC, abstractmethod
from typing import List, Optional


class ForumRepository(ABC):
    @abstractmethod
    def get_all_topics(self) -> List[dict]:
        raise NotImplementedError

    @abstractmethod
    def get_topics_by_likes(self) -> List[dict]:
        raise NotImplementedError

    @abstractmethod
    def get_topic_detail(self, topic_id: int) -> Optional[dict]:
        raise NotImplementedError

    @abstractmethod
    def get_topic_title(self, topic_id: int) -> Optional[str]:
        raise NotImplementedError

    @abstractmethod
    def create_topic(
        self,
        category: str,
        title: str,
        content: str,
        author: str,
        time: str,
        date: str,
        likes: int,
        dislikes: int,
        comments: int,
    ) -> int:
        raise NotImplementedError

    @abstractmethod
    def update_topic(self, topic_id: int, title: str, content: str, category: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_topic(self, topic_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_comments_for_topic(self, topic_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def toggle_topic_reaction(self, topic_id: int, user_id: int, reaction: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_user_topic_reaction(self, topic_id: int, user_id: int) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_comment(self, comment_id: int) -> Optional[dict]:
        raise NotImplementedError

    @abstractmethod
    def get_comments_for_topic(self, topic_id: int) -> List[dict]:
        raise NotImplementedError

    @abstractmethod
    def create_comment(
        self,
        topic_id: int,
        content: str,
        author: str,
        date: str,
        time: str,
        topics_id: int,
        receiver: Optional[str],
        is_answer: Optional[bool],
        parent_id: Optional[int],
    ) -> dict:
        raise NotImplementedError

    @abstractmethod
    def update_comment_content(self, comment_id: int, content: str, actor: Optional[str] = None) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_comment(self, comment_id: int, topic_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def toggle_comment_reaction(self, comment_id: int, user_id: int, reaction: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def update_author_name(self, old_name: str, new_name: str) -> None:
        raise NotImplementedError
