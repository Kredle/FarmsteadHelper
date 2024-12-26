from django.db import models

class Animal(models.Model):
    id = models.AutoField(primary_key=True)
    common_name = models.CharField(max_length=100)
    image_url = models.TextField(verbose_name="Зображення", null=True, blank=True, db_column = 'image')
    category = 'animals'

    class Meta:
        managed = False
        db_table = 'animals'

class Plant(models.Model):
    id = models.AutoField(primary_key=True)
    common_name = models.CharField(max_length=100, db_column = 'name')
    image_url = models.TextField(verbose_name="Зображення", null=True, blank=True, db_column = 'image')
    category = 'flowers'

    class Meta:
        managed = False
        db_table = 'plants'

class Vegetable(models.Model):
    id = models.AutoField(primary_key=True, db_column = 'idSort')
    common_name = models.CharField(max_length=100, db_column = 'Name')
    image_url = models.TextField(verbose_name="Зображення", null=True, blank=True, db_column = 'Image')
    category = 'vegetables'

    class Meta:
        managed = False
        db_table = 'sorts_veg'

class Tree(models.Model):
    id = models.AutoField(primary_key=True, db_column = 'idSort')
    common_name = models.CharField(max_length=100, db_column = 'Sort')
    image_url = models.TextField(verbose_name="Зображення плоду", null=True, blank=True , db_column = 'Image_fruit')
    category = 'trees'

    class Meta:
        managed = False
        db_table = 'sorts'