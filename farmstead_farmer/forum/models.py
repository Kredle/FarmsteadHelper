from django.db import models

class Topic(models.Model):
    idTopic = models.AutoField(primary_key=True, db_column = 'idTopic')
    Content = models.TextField(db_column = 'Content')
    Likes = models.IntegerField(db_column = 'Likes')
    Dislikes = models.IntegerField(db_column = 'Dislikes')
    Date = models.DateField(db_column = 'Date')
    Time = models.TimeField(db_column = 'Time')
    Title = models.TextField(db_column = 'Title')
    Category = models.CharField(max_length=45, db_column = 'Category')
    Comments = models.IntegerField(db_column = 'Comments')
    Author = models.TextField(db_column = 'Author')
    Likes_list =models.JSONField(default=list, blank=True)
    Dislikes_list = models.JSONField(default=list, blank=True)


    class Meta:
        managed = False
        db_table = 'topics'

class Comment(models.Model):
    idComments = models.AutoField(primary_key=True, db_column = 'idComments')
    Content = models.TextField(db_column = 'Content')
    Likes = models.IntegerField(db_column = 'Likes')
    Dislikes = models.IntegerField(db_column = 'Dislikes')
    Date = models.DateField(db_column = 'Date')
    Time = models.TimeField(db_column = 'Time')
    Comments = models.IntegerField(db_column = 'Comments')
    Author = models.TextField(db_column = 'Author')
    Topics_id = models.IntegerField(db_column = 'Topics_idTopic')
    Receiver = models.TextField(db_column = 'Receiver')
    IsAnswer = models.BooleanField(null=True, db_column = 'IsAnswer')
    Likes_list =models.JSONField(default=list, blank=True)
    Dislikes_list = models.JSONField(default=list, blank=True)
    ParentId = models.IntegerField(db_column='ParentId')
    class Meta:
        managed = False
        db_table = 'comments'
    
class User(models.Model):
    Password = models.CharField(max_length=128, db_column='password')
    Username = models.CharField(max_length=150, db_column='username')
    Staff = models.BooleanField(db_column='is_staff')
    Active = models.BooleanField(db_column='is_active')
    Email = models.CharField(max_length=254, db_column='email')
    Favorites = models.JSONField(db_column='favorites')

    class Meta:
        managed = False
        db_table = 'api_customuser'
# Create your models here.
