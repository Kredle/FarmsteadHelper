from django.db import models

class Vegetables(models.Model):
    idVeg = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=150, null=True, blank=True)
    Type = models.CharField(max_length=45, null=True, blank=True)
    Protein_content = models.CharField(max_length=45, null=True, blank=True)
    Fat_content = models.CharField(max_length=45, null=True, blank=True, db_column = 'Fat_сontent')
    Carb_content = models.CharField(max_length=45, null=True, blank=True)
    Vitamins = models.TextField(null=True, blank=True)
    Minerals = models.TextField(null=True, blank=True)
    Plant_time = models.CharField(max_length=45, null=True, blank=True)
    Compatibility = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'vegetables'

class SortsVeg(models.Model):
    idSort = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=80, null=True, blank=True)
    Veg_Color = models.CharField(max_length=45, null=True, blank=True)
    Ripe_time = models.CharField(max_length=45, null=True, blank=True)
    Weight = models.CharField(max_length=45, null=True, blank=True)
    Usage = models.TextField(null=True, blank=True)
    Image = models.TextField(null=True, blank=True)
    Discription = models.TextField(null=True, blank=True, db_column = 'Discription')
    vegetables_idVeg = models.ForeignKey(Vegetables, on_delete=models.CASCADE, db_column='vegetables_idVeg')

    class Meta:
        managed = False
        db_table = 'sorts_veg'

class FertilizerVeg(models.Model):
    idFertilizer = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=80, null=True, blank=True)
    Time_Fertilizer = models.CharField(max_length=45, null=True, blank=True)
    Type = models.CharField(max_length=45, null=True, blank=True)
    Fertilizer_Discription = models.TextField(null=True, blank=True, db_column = 'Frtilizer_Discription')

    class Meta:
        managed = False
        db_table = 'fertilizer_veg'

class DiseasesVeg(models.Model):
    idDisease = models.AutoField(primary_key=True)
    Disease_Name = models.CharField(max_length=45, null=True, blank=True)
    Disease_Discription = models.TextField(null=True, blank=True)
    Disease_Treatment = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'diseases_veg'
