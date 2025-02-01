from django.db import models

class id_tree(models.Model):
    id = models.AutoField(primary_key=True, db_column = 'idTree')

    class Meta:
        managed = False
        db_table = 'tree'

class id_vegetable(models.Model):
    id = models.AutoField(primary_key=True, db_column = 'idVeg')

    class Meta:
        managed = False
        db_table = 'vegetables'


class Animal(models.Model):
    sort_id = models.AutoField(primary_key=True, db_column = 'id')
    common_name = models.CharField(max_length=100, db_column="common_name")
    image_url = models.TextField(verbose_name="Зображення", null=True, blank=True, db_column = 'image')
    category = 'animals'

    class Meta:
        managed = False
        db_table = 'animals'

class Plant(models.Model):
    sort_id = models.AutoField(primary_key=True, db_column = 'id')
    common_name = models.CharField(max_length=100, db_column = 'name')
    image_url = models.TextField(verbose_name="Зображення", null=True, blank=True, db_column = 'image')
    category = 'flowers'

    class Meta:
        managed = False
        db_table = 'plants'

class Vegetable(models.Model):
    sort_id = models.AutoField(primary_key=True, db_column = 'idSort')
    common_name = models.CharField(max_length=100, db_column = 'Name')
    image_url = models.TextField(verbose_name="Зображення", null=True, blank=True, db_column = 'Image')
    vegetable = models.ForeignKey(id_vegetable, on_delete=models.CASCADE, db_column='vegetables_idVeg')
    category = 'vegetables'

    class Meta:
        managed = False
        db_table = 'sorts_veg'

class Tree(models.Model):
    sort_id = models.AutoField(primary_key=True, db_column = 'idSort')
    common_name = models.CharField(max_length=100, db_column = 'Sort')
    image_url = models.TextField(verbose_name="Зображення плоду", null=True, blank=True , db_column = 'Image_fruit')
    tree = models.ForeignKey(id_tree, on_delete=models.CASCADE, related_name="sorts", verbose_name="Дерево",db_column='tree_idTree')
    category = 'trees'

    class Meta:
        managed = False
        db_table = 'sorts'

class FindTree(models.Model):
    idTree = models.IntegerField(primary_key=True, db_column = 'idTree')
    common_name2 = models.CharField(max_length=100, db_column = 'Name')
    image_url = models.TextField(verbose_name="Зображення плоду", null=True, blank=True , db_column = 'Image_tree')

    class Meta:
        managed = False
        db_table = 'tree'

class FindVeg(models.Model):
    idVeg = models.IntegerField(primary_key=True, db_column = 'idVeg')
    common_name2 = models.CharField(max_length=100, db_column = 'Name')
    image_url = models.TextField(verbose_name="Зображення", null=True, blank=True, db_column = 'Image')

    class Meta:
        managed = False
        db_table = 'vegetables'

class FindVeg_sort(models.Model):
    idVeg_sort = models.IntegerField(primary_key=True, db_column = 'idSort')
    common_name = models.CharField(max_length=100, db_column = 'Name')
    image_url = models.TextField(verbose_name="Зображення", null=True, blank=True, db_column = 'Image')
    idVeg = models.IntegerField(db_column = 'vegetables_idVeg')
    class Meta:
        managed = False
        db_table = 'sorts_veg'

class FindTree_sort(models.Model):
    idTree_sort = models.IntegerField(primary_key=True, db_column = 'idSort')
    common_name = models.CharField(max_length=100, db_column = 'Sort')
    image_url = models.TextField(verbose_name="Зображення плоду", null=True, blank=True , db_column = 'Image_fruit')
    idTree = models.IntegerField(db_column = 'tree_idTree')
    class Meta:
        managed = False
        db_table = 'sorts'

