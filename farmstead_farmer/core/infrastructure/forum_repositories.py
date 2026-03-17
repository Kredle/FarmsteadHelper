import json
from typing import List, Optional

from forum.models import Comment, Topic

from core.domain.exceptions import DomainError
from core.domain.forum_repositories import ForumRepository


class TopicNotFoundError(DomainError):
    pass


class CommentNotFoundError(DomainError):
    pass


class DjangoForumRepository(ForumRepository):
    def get_all_topics(self) -> List[dict]:
        return list(Topic.objects.all().values())

    def get_topics_by_likes(self) -> List[dict]:
        return list(Topic.objects.all().order_by("-Likes").values())

    def get_topic_detail(self, topic_id: int) -> Optional[dict]:
        try:
            topic = Topic.objects.get(pk=topic_id)
        except Topic.DoesNotExist:
            return None
        return {
            "id": topic.idTopic,
            "title": topic.Title,
            "content": topic.Content,
            "category": topic.Category,
            "author": topic.Author,
            "date": str(topic.Date),
            "time": str(topic.Time),
            "likes": topic.Likes,
            "dislikes": topic.Dislikes,
            "comments": topic.Comments,
            "likes_list": topic.Likes_list,
            "dislikes_list": topic.Dislikes_list,
        }

    def get_topic_title(self, topic_id: int) -> Optional[str]:
        try:
            return Topic.objects.values_list("Title", flat=True).get(idTopic=topic_id)
        except Topic.DoesNotExist:
            return None

    def create_topic(self, category, title, content, author, time, date, likes, dislikes, comments) -> int:
        topic = Topic.objects.create(
            Category=category,
            Title=title,
            Content=content,
            Author=author,
            Time=time,
            Date=date,
            Likes=likes,
            Dislikes=dislikes,
            Comments=comments,
            Likes_list="[]",
            Dislikes_list="[]",
        )
        return topic.idTopic

    def update_topic(self, topic_id: int, title: str, content: str, category: str) -> None:
        try:
            topic = Topic.objects.get(idTopic=topic_id)
        except Topic.DoesNotExist as exc:
            raise TopicNotFoundError(str(exc))
        topic.Title = title
        topic.Content = content
        topic.Category = category
        topic.save()

    def delete_topic(self, topic_id: int) -> None:
        Topic.objects.filter(idTopic=topic_id).delete()

    def delete_comments_for_topic(self, topic_id: int) -> None:
        Comment.objects.filter(Topics_id=topic_id).delete()

    @staticmethod
    def _normalize_lists(instance) -> None:
        if not isinstance(instance.Likes_list, list):
            try:
                instance.Likes_list = json.loads(instance.Likes_list)
            except (json.JSONDecodeError, TypeError):
                instance.Likes_list = []
        if not isinstance(instance.Dislikes_list, list):
            try:
                instance.Dislikes_list = json.loads(instance.Dislikes_list)
            except (json.JSONDecodeError, TypeError):
                instance.Dislikes_list = []

    def toggle_topic_reaction(self, topic_id: int, user_id: int, reaction: str) -> dict:
        try:
            topic = Topic.objects.get(idTopic=topic_id)
        except Topic.DoesNotExist as exc:
            raise TopicNotFoundError(str(exc))
        self._normalize_lists(topic)

        if reaction == "reset":
            if user_id in topic.Likes_list:
                topic.Likes_list.remove(user_id)
                topic.Likes -= 1
            if user_id in topic.Dislikes_list:
                topic.Dislikes_list.remove(user_id)
                topic.Dislikes -= 1
        elif reaction == "like":
            if user_id not in topic.Likes_list:
                topic.Likes_list.append(user_id)
                topic.Likes += 1
            if user_id in topic.Dislikes_list:
                topic.Dislikes_list.remove(user_id)
                topic.Dislikes -= 1
        elif reaction == "dislike":
            if user_id not in topic.Dislikes_list:
                topic.Dislikes_list.append(user_id)
                topic.Dislikes += 1
            if user_id in topic.Likes_list:
                topic.Likes_list.remove(user_id)
                topic.Likes -= 1

        topic.save()
        return {
            "Likes": topic.Likes,
            "Dislikes": topic.Dislikes,
            "Likes_list": topic.Likes_list,
            "Dislikes_list": topic.Dislikes_list,
        }

    def get_user_topic_reaction(self, topic_id: int, user_id: int) -> str:
        try:
            topic = Topic.objects.get(idTopic=topic_id)
        except Topic.DoesNotExist as exc:
            raise TopicNotFoundError(str(exc))
        self._normalize_lists(topic)
        if user_id in topic.Likes_list:
            return "like"
        if user_id in topic.Dislikes_list:
            return "dislike"
        return "reset"

    def get_comment(self, comment_id: int) -> Optional[dict]:
        try:
            comment = Comment.objects.get(idComments=comment_id)
        except Comment.DoesNotExist:
            return None
        return {
            "id": comment.idComments,
            "Author": comment.Author,
            "Content": comment.Content,
            "Date": comment.Date,
            "Time": comment.Time,
            "ParentId": comment.ParentId,
            "Comments": comment.Comments,
            "Topics_id": comment.Topics_id,
            "absolute_url": comment.get_absolute_url(),
        }

    def get_comments_for_topic(self, topic_id: int) -> List[dict]:
        return list(
            Comment.objects.filter(Topics_id=topic_id).values(
                "Author",
                "Content",
                "Likes",
                "Dislikes",
                "Comments",
                "Date",
                "Time",
                "idComments",
                "ParentId",
            )
        )

    def create_comment(self, topic_id, content, author, date, time, topics_id, receiver, is_answer, parent_id) -> dict:
        try:
            topic = Topic.objects.get(idTopic=topic_id)
        except Topic.DoesNotExist as exc:
            raise TopicNotFoundError(str(exc))

        parent_comment = Comment.objects.filter(idComments=parent_id).first() if parent_id else None
        comment = Comment(
            Content=content,
            Likes=0,
            Dislikes=0,
            Comments=0,
            Date=date,
            Time=time,
            Author=author,
            Topics_id=topics_id,
            Receiver=receiver,
            IsAnswer=is_answer,
            ParentId=parent_id,
        )
        topic.Comments += 1
        topic.save()
        if parent_comment:
            parent_comment.Comments += 1
            parent_comment.save()
        comment.save()
        return {
            "status": "success",
            "id": comment.idComments,
            "Author": comment.Author,
            "Content": comment.Content,
            "Date": comment.Date,
            "Time": comment.Time,
            "ParentId": parent_id,
            "Comments": 0,
        }

    def update_comment_content(self, comment_id: int, content: str, actor: Optional[str] = None) -> None:
        try:
            comment = Comment.objects.get(idComments=comment_id)
        except Comment.DoesNotExist as exc:
            raise CommentNotFoundError(str(exc))
        if actor is not None and comment.Author != actor:
            raise PermissionError("Not the comment author")
        comment.Content = content
        comment.save()

    def delete_comment(self, comment_id: int, topic_id: int) -> None:
        try:
            comment = Comment.objects.get(idComments=comment_id)
            topic = Topic.objects.get(idTopic=topic_id)
        except (Comment.DoesNotExist, Topic.DoesNotExist) as exc:
            raise DomainError(str(exc))
        topic.Comments = int(topic.Comments) - 1
        topic.save()
        comment.delete()

    def toggle_comment_reaction(self, comment_id: int, user_id: int, reaction: str) -> dict:
        try:
            comment = Comment.objects.get(idComments=comment_id)
        except Comment.DoesNotExist as exc:
            raise CommentNotFoundError(str(exc))
        self._normalize_lists(comment)

        if reaction == "reset":
            if user_id in comment.Likes_list:
                comment.Likes_list.remove(user_id)
                comment.Likes -= 1
            if user_id in comment.Dislikes_list:
                comment.Dislikes_list.remove(user_id)
                comment.Dislikes -= 1
        elif reaction == "like":
            is_inside = user_id in comment.Likes_list
            if not is_inside:
                comment.Likes_list.append(user_id)
                comment.Likes += 1
            if user_id in comment.Dislikes_list:
                comment.Dislikes_list.remove(user_id)
                comment.Dislikes -= 1
            if is_inside:
                comment.Likes_list.remove(user_id)
                comment.Likes -= 1
        elif reaction == "dislike":
            is_inside = user_id in comment.Dislikes_list
            if not is_inside:
                comment.Dislikes_list.append(user_id)
                comment.Dislikes += 1
            if user_id in comment.Likes_list:
                comment.Likes_list.remove(user_id)
                comment.Likes -= 1
            if is_inside:
                comment.Dislikes_list.remove(user_id)
                comment.Dislikes -= 1

        comment.save()
        return {
            "Likes": comment.Likes,
            "Dislikes": comment.Dislikes,
            "Likes_list": comment.Likes_list,
            "Dislikes_list": comment.Dislikes_list,
        }

    def update_author_name(self, old_name: str, new_name: str) -> None:
        Topic.objects.filter(Author=old_name).update(Author=new_name)
        Comment.objects.filter(Author=old_name).update(Author=new_name)
