from django.db import models

class Plants(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.CharField(max_length=5)
    end_date = models.CharField(max_length=5)

    class Meta:
        managed = False
        db_table = 'plants'

class Veg(models.Model):
    idVeg = models.AutoField(primary_key=True)
    Plant_time_From1 = models.CharField(max_length=5)
    Plant_time_From2 = models.CharField(max_length=5, db_column = 'Plant_time_To2')
    Plant_time_To2 = models.CharField(max_length=5, db_column = 'Plant_time_From2')
    Plant_time_To1 = models.CharField(max_length=5)

    class Meta:
        managed = False
        db_table = 'vegetables'

class Sort_veg(models.Model):
    id = models.AutoField(primary_key=True,db_column='idSort')
    Ripe_time_From1 = models.CharField(max_length=5)
    Ripe_time_To1 = models.CharField(max_length=5)
    Ripe_time_From2 = models.CharField(max_length=5)
    Ripe_time_To2 = models.CharField(max_length=5)
    Name = models.CharField(max_length=100)
    vegetables_idVeg = models.ForeignKey(Veg, on_delete=models.CASCADE, db_column='vegetables_idVeg')

    class Meta:
        managed = False
        db_table = 'sorts_veg'

class Tree(models.Model):
    idTree = models.AutoField(primary_key=True)
    Scope_of_bloom_From = models.CharField(max_length=5)
    Scope_of_bloom_To = models.CharField(max_length=5)
    Ripe_Time_From = models.CharField(max_length=5)
    Ripe_Time_To = models.CharField(max_length=5)

    class Meta:
        managed = False
        db_table = 'tree'

class Sort_tree(models.Model):
    id = models.AutoField(primary_key=True,db_column='idSort')
    Usage = models.CharField(max_length=100)
    sort = models.CharField(max_length=150, verbose_name="Сорт", null=True, blank=True)
    tree = models.ForeignKey(Tree, on_delete=models.CASCADE, related_name="sorts", verbose_name="Дерево",db_column='tree_idTree')

    class Meta:
        managed = False
        db_table = 'sorts'


class Planting(models.Model):
    id = models.AutoField(primary_key=True,db_column='idPlantting')
    Plant_time_From = models.CharField(max_length=5)
    Plant_time_To =  models.CharField(max_length=5)

    class Meta:
        managed = False
        db_table = 'planting'

class Cutting(models.Model):
    id = models.AutoField(primary_key=True,db_column='idCutting')
    Cutting_time_From = models.CharField(max_length=5)
    Cutting_time_To =  models.CharField(max_length=5)

    class Meta:
        managed = False
        db_table = 'cutting'


class Fertilizer(models.Model):
    id = models.AutoField(primary_key=True,db_column='idFertilizer')
    Fertilizer_date_From1 = models.CharField(max_length=5)
    Fertilizer_date_To1 =  models.CharField(max_length=5)
    Fertilizer_date_From2 = models.CharField(max_length=5)
    Fertilizer_date_To2 =  models.CharField(max_length=5)

    class Meta:
        managed = False
        db_table = 'fertilizer'


class Fertilizer_veg(models.Model):
    id = models.AutoField(primary_key=True,db_column='idFertilizer')
    Time_Fertilizer_From1 = models.CharField(max_length=5)
    Time_Fertilizer_To1 =  models.CharField(max_length=5)
    Time_Fertilizer_From2 = models.CharField(max_length=5)
    Time_Fertilizer_To2 =  models.CharField(max_length=5)

    class Meta:
        managed = False
        db_table = 'fertilizer_veg'





