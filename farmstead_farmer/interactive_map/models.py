from django.db import models
from api.models import CustomUser
class Map(models.Model):
    User_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="api_customuser_id",db_column='api_customuser_id')
    id = models.IntegerField(primary_key=True, db_column = 'idInteractive')
    data = models.JSONField(db_column = 'map')
    class Meta:
        managed = False
        db_table = 'interactive_map'
