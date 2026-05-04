import json
from typing import List, Optional
from datetime import date, datetime, time as dt_time
from django.db.models.expressions import RawSQL
from forum.models import Comment, Topic
from django.db.models import F
from core.domain.exceptions import DomainError
from core.domain.forum_repositories import ForumRepository
from forum.models import Notification
from api.models import CustomUser
from django.utils.timezone import now
from datetime import timedelta

class TopicNotFoundError(DomainError):
    pass


class CommentNotFoundError(DomainError):
    pass


class DjangoForumRepository(ForumRepository):
    UKRAINIAN_MONTHS_GENITIVE = {
        1: "січня",
        2: "лютого",
        3: "березня",
        4: "квітня",
        5: "травня",
        6: "червня",
        7: "липня",
        8: "серпня",
        9: "вересня",
        10: "жовтня",
        11: "листопада",
        12: "грудня",
    }

    # --------------------------- Допоміжні методи ---------------------------------
    def _format_ukrainian_date(self, value) -> str:
        """Форматує дату у вигляд: 01 травня 2026 р."""
        if value is None:
            return ""

        if isinstance(value, datetime):
            value = value.date()

        if isinstance(value, date):
            month_name = self.UKRAINIAN_MONTHS_GENITIVE.get(value.month, "")
            return f"{value.day:02d} {month_name} {value.year} р.".strip()

        return str(value)

    def _format_time(self, value) -> str:
        """Форматує час у вигляд: 14:35."""
        if value is None:
            return ""

        if isinstance(value, datetime):
            value = value.time()

        if isinstance(value, dt_time):
            return value.strftime("%H:%M")

        value_str = str(value)
        parts = value_str.split(':')
        if len(parts) >= 2:
            return f"{parts[0].zfill(2)}:{parts[1].zfill(2)}"
        return value_str

    def _getTopic(self):
        """Повертає 'Stream' (QuerySet) для тем з безпечними JSON полями."""
        return Topic.objects.defer("Likes_list", "Dislikes_list").annotate(
            l_raw=RawSQL(' "Likes_list"::text ', []),
            d_raw=RawSQL(' "Dislikes_list"::text ', [])
        )

    def _getComment(self):
        """Повертає 'Stream' (QuerySet) для коментарів з безпечними JSON полями."""
        return Comment.objects.defer("Likes_list", "Dislikes_list").annotate(
            l_raw=RawSQL(' "Likes_list"::text ', []),
            d_raw=RawSQL(' "Dislikes_list"::text ', [])
        )

    def _get_clean_json_list(self, item, raw_field_name: str) -> list:
        """Приватний парсер для перетворення тексту RawSQL у Python list."""
        raw_val = getattr(item, raw_field_name, None)
        if raw_val and isinstance(raw_val, str) and raw_val != 'null':
            try:
                return json.loads(raw_val)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    def _map_topics(self, topics_qs) -> dict:
        """Перетворює QuerySet тем у словник із ключем 'topics'."""
        return {
            "topics": [
                {
                    "idTopic": t.idTopic,
                    "Title": t.Title,
                    "Content": t.Content,
                    "Category": t.Category,
                    "Likes": t.Likes,
                    "Dislikes": t.Dislikes,
                    "Date": self._format_ukrainian_date(t.Date),
                    "Time": self._format_time(t.Time),
                    "Author": str(t.Author),
                    "Comments": t.Comments,
                    "Likes_list": self._get_clean_json_list(t, 'l_raw'),
                    "Dislikes_list": self._get_clean_json_list(t, 'd_raw'),
                } for t in topics_qs
            ]
        }

    def _map_comments(self, comments_qs) -> dict:
        """Перетворює QuerySet коментарів у словник із ключем 'comments'."""
        return {
            "comments": [
                {
                    "idComments": c.idComments,
                    "Author": str(c.Author),
                    "Content": c.Content,
                    "Likes": c.Likes,
                    "Dislikes": c.Dislikes,
                    "Comments": c.Comments,
                    "Date": self._format_ukrainian_date(c.Date),
                    "Time": self._format_time(c.Time),
                    "ParentId": c.ParentId,
                    "Likes_list": self._get_clean_json_list(c, 'l_raw'),
                    "Dislikes_list": self._get_clean_json_list(c, 'd_raw'),
                } for c in comments_qs
            ]
        }
    # -----------------------------------------------------------------------------------
    def get_all_topics(self) -> dict:
        topics = self._getTopic()
        
        return self._map_topics(topics)


    def get_topics_by_likes(self) -> dict:
        topics = self._getTopic().order_by("-Likes")
        
        return self._map_topics(topics)


    def get_topic_detail(self, topic_id: int) -> Optional[dict]:
        try:
            t = self._getTopic().get(pk=topic_id)
        except Topic.DoesNotExist:
            return None

        return self._map_topics([t])["topics"][0]
    
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
        updated_count = Topic.objects.filter(idTopic=topic_id).update(
            Title=title,
            Content=content,
            Category=category
        )

        if updated_count == 0:
            raise TopicNotFoundError(f"Topic with id {topic_id} not found")

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
            topic_data = self.get_topic_detail(topic_id)
            if not topic_data:
                raise TopicNotFoundError(f"Topic {topic_id} not found")
            
            l_list = topic_data["Likes_list"]
            if isinstance(l_list, str):
                l_list = json.loads(l_list) if l_list and l_list != 'null' else []
            
            d_list = topic_data["Dislikes_list"]
            if isinstance(d_list, str):
                d_list = json.loads(d_list) if d_list and d_list != 'null' else []
            try:
                user_id = int(user_id)
            except (ValueError, TypeError):
                raise DomainError("Invalid user ID format")
            likes_count = topic_data["Likes"]
            dislikes_count = topic_data["Dislikes"]

            if reaction == "reset":
                if user_id in l_list:
                    l_list.remove(user_id)
                    likes_count -= 1
                if user_id in d_list:
                    d_list.remove(user_id)
                    dislikes_count -= 1
            elif reaction == "like":
                if user_id not in l_list:
                    l_list.append(user_id)
                    likes_count += 1
                if user_id in d_list:
                    d_list.remove(user_id)
                    dislikes_count -= 1
            elif reaction == "dislike":
                if user_id not in d_list:
                    d_list.append(user_id)
                    dislikes_count += 1
                if user_id in l_list:
                    l_list.remove(user_id)
                    likes_count -= 1

            Topic.objects.filter(idTopic=topic_id).update(
                Likes=likes_count,
                Dislikes=dislikes_count,
                Likes_list=l_list,
                Dislikes_list=d_list
            )

            return {
                "Likes": likes_count,
                "Dislikes": dislikes_count,
                "Likes_list": l_list,
                "Dislikes_list": d_list,
            }

        except Exception as e:
            raise DomainError(str(e))

    def get_user_topic_reaction(self, topic_id: int, user_id: int) -> str:
        topic_qs = Topic.objects.filter(idTopic=topic_id)

        # Перевіряємо Likes_list
        # Додаємо умову: json_typeof("Likes_list") = 'array'
        check_like = topic_qs.annotate(
            is_liked=RawSQL(
                '''
                EXISTS (
                    SELECT 1 
                    FROM json_array_elements_text(
                        CASE 
                            WHEN json_typeof("Likes_list"::json) = 'array' THEN "Likes_list"::json 
                            ELSE '[]'::json 
                        END
                    ) AS elem 
                    WHERE elem = %s
                )
                ''', 
                [str(user_id)]
            )
        ).values_list('is_liked', flat=True).first()

        if check_like:
            return "like"

        # Перевіряємо Dislikes_list аналогічно
        check_dislike = topic_qs.annotate(
            is_disliked=RawSQL(
                '''
                EXISTS (
                    SELECT 1 
                    FROM json_array_elements_text(
                        CASE 
                            WHEN json_typeof("Dislikes_list"::json) = 'array' THEN "Dislikes_list"::json 
                            ELSE '[]'::json 
                        END
                    ) AS elem 
                    WHERE elem = %s
                )
                ''', 
                [str(user_id)]
            )
        ).values_list('is_disliked', flat=True).first()

        if check_dislike:
            return "dislike"

        return "reset"

    def get_comment(self, comment_id: int) -> Optional[dict]:
        try:
            c = self._getComment().get(idComments=comment_id)

            comment_dict = self._map_comments([c])["comments"][0]
            
            comment_dict["Topics_id"] = c.Topics_id
            comment_dict["absolute_url"] = c.get_absolute_url()
            
            return comment_dict
            
        except (Comment.DoesNotExist, IndexError):
            return None

    def get_comments_for_topic(self, topic_id: int) -> dict:
        comments = self._getComment().filter(Topics_id=topic_id)
        
        return self._map_comments(comments)


    from django.db.models import F

    def create_comment(self, topic_id, content, author, date, time, topics_id, receiver, is_answer, parent_id) -> dict:
        try:
            is_answer_int = 1 if is_answer else 0
            comment = Comment.objects.create(
                Content=content,
                Likes=0,
                Dislikes=0,
                Comments=0,
                Date=date,
                Time=time,
                Author=author,
                Topics_id=topics_id,
                Receiver=receiver,
                IsAnswer=is_answer_int,
                ParentId=parent_id,
                Likes_list=[],    
                Dislikes_list=[]  
            )

            updated_topic = Topic.objects.filter(idTopic=topic_id).update(
                Comments=F('Comments') + 1
            )
            
            if updated_topic == 0:
                raise TopicNotFoundError(f"Topic {topic_id} not found")

            if parent_id:
                Comment.objects.filter(idComments=parent_id).update(
                    Comments=F('Comments') + 1
                )

            return {
                "status": "success",
                "id": comment.idComments,
                "Author": str(comment.Author),
                "Content": comment.Content,
                "Date": self._format_ukrainian_date(comment.Date),
                "Time": self._format_time(comment.Time),
                "ParentId": parent_id,
                "Comments": 0,
            }

        except Exception as e:
            raise DomainError(str(e))

    def update_comment_content(self, comment_id: int, content: str, actor: Optional[str] = None) -> None:
        try:
            comment_qs = self._getComment().filter(idComments=comment_id)
            comment = comment_qs.first()

            if not comment:
                raise CommentNotFoundError(f"Comment {comment_id} not found")

            if actor is not None and str(comment.Author) != actor:
                raise PermissionError("Not the comment author")

            comment_qs.update(Content=content)

        except Exception as e:
            if isinstance(e, (CommentNotFoundError, PermissionError)):
                raise e
            raise DomainError(str(e))

    def delete_comment(self, comment_id: int, topic_id: int) -> None:
        try:
            if not Topic.objects.filter(idTopic=topic_id).exists():
                raise DomainError(f"Topic {topic_id} not found")

            root_comment_id = Comment.objects.filter(
                idComments=comment_id,
                Topics_id=topic_id,
            ).values_list('idComments', flat=True).first()
            if root_comment_id is None:
                raise DomainError(f"Comment {comment_id} not found")

            ids_to_delete = {root_comment_id}
            frontier = [root_comment_id]

            # Видаляємо всю гілку: коментар і всіх його нащадків будь-якої глибини
            while frontier:
                child_ids = list(
                    Comment.objects.filter(
                        Topics_id=topic_id,
                        ParentId__in=frontier,
                    ).values_list('idComments', flat=True)
                )
                frontier = [cid for cid in child_ids if cid not in ids_to_delete]
                ids_to_delete.update(frontier)

            comments_qs = Comment.objects.filter(
                Topics_id=topic_id,
                idComments__in=ids_to_delete,
            )
            deleted_count = comments_qs.count()
            if deleted_count > 0:
                comments_qs._raw_delete(comments_qs.db)

            if deleted_count == 0:
                raise DomainError(f"Comment {comment_id} not found")

            Topic.objects.filter(idTopic=topic_id).update(
                Comments=F('Comments') - deleted_count
            )

        except Exception as e:
            if isinstance(e, DomainError):
                raise e
            raise DomainError(str(e))

    def toggle_comment_reaction(self, comment_id: int, user_id: int, reaction: str) -> dict:
        try:
            comment_data = self.get_comment(comment_id)
            if not comment_data:
                raise CommentNotFoundError(f"Comment {comment_id} not found")
            
            l_list = comment_data["Likes_list"]
            if isinstance(l_list, str):
                l_list = json.loads(l_list) if l_list and l_list != 'null' else []
            
            d_list = comment_data["Dislikes_list"]
            if isinstance(d_list, str):
                d_list = json.loads(d_list) if d_list and d_list != 'null' else []
            try:
                user_id = int(user_id)
            except (ValueError, TypeError):
                raise DomainError("Invalid user ID format")
            likes_count = comment_data["Likes"]
            dislikes_count = comment_data["Dislikes"]

            if reaction == "reset":
                if user_id in l_list:
                    l_list.remove(user_id)
                    likes_count -= 1
                if user_id in d_list:
                    d_list.remove(user_id)
                    dislikes_count -= 1
            elif reaction == "like":
                is_inside = user_id in l_list
                if not is_inside:
                    l_list.append(user_id)
                    likes_count += 1
                if user_id in d_list:
                    d_list.remove(user_id)
                    dislikes_count -= 1
                if is_inside:
                    l_list.remove(user_id)
                    likes_count -= 1
            elif reaction == "dislike":
                is_inside = user_id in d_list
                if not is_inside:
                    d_list.append(user_id)
                    dislikes_count += 1
                if user_id in l_list:
                    l_list.remove(user_id)
                    likes_count -= 1
                if is_inside:
                    d_list.remove(user_id)
                    dislikes_count -= 1

            Comment.objects.filter(idComments=comment_id).update(
                Likes=likes_count,
                Dislikes=dislikes_count,
                Likes_list=l_list,
                Dislikes_list=d_list
            )

            return {
                "Likes": likes_count,
                "Dislikes": dislikes_count,
                "Likes_list": l_list,
                "Dislikes_list": d_list,
            }

        except Exception as e:
            if isinstance(e, CommentNotFoundError):
                raise e
            raise DomainError(str(e))

    def update_author_name(self, old_name: str, new_name: str) -> None:
        Topic.objects.filter(Author=old_name).update(Author=new_name)
        Comment.objects.filter(Author=old_name).update(Author=new_name)

    def create_notification(self, owner_username: str, content: str, link: str) -> None:
        try:
            user = CustomUser.objects.get(username=owner_username)
            Notification.objects.create(owner=user, content=content, link=link)
        except CustomUser.DoesNotExist:
            pass

    def get_notifications(self, username: str) -> list:
        # Повертаємо тільки непрочитані сповіщення
        notifs = Notification.objects.filter(owner__username=username, is_read=False).order_by('-created_at')
        return [{
            "id": n.idNotification,  # JS очікує "id"
            "content": n.content,
            "link": n.link
        } for n in notifs]

    def delete_old_notifications(self) -> None:
        Notification.objects.filter(created_at__lt=now() - timedelta(days=7)).delete()

    def mark_notification_as_read(self, notification_id: int, username: str) -> bool:
        # Оновлюємо статус, перевіряючи, що сповіщення належить користувачу
        updated_count = Notification.objects.filter(
            pk=notification_id, 
            owner__username=username).update(is_read=True)
        return updated_count > 0
