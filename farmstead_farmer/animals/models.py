from django.db import models

class Animal_main(models.Model):
    idAni = models.AutoField(primary_key=True, db_column='idAni')
    Name = models.CharField(max_length=150, null=True, blank=True, db_column='Name')
    Image = models.TextField(null=True, blank=True, db_column='Image')
    
    class Meta:
        managed = False
        db_table = 'animals_animal_main'

class Animal(models.Model):
    id = models.AutoField(primary_key=True, db_column="id")
    scientific_name = models.CharField(max_length=150, db_column="scientific_name")
    common_name = models.CharField(max_length=100, blank=True, null=True, db_column="common_name")
    class_field = models.CharField(db_column='class', max_length=50, blank=True, null=True) 
    genus = models.CharField(max_length=100, blank=True, null=True, db_column="genus")
    family = models.CharField(max_length=100, blank=True, null=True, db_column="family")
    size = models.CharField(max_length=100, blank=True, null=True, db_column="size")
    weight = models.CharField(max_length=50, blank=True, null=True, db_column="weight")
    lifespan = models.CharField(max_length=50, blank=True, null=True, db_column="lifespan")
    habitat = models.TextField(blank=True, null=True, db_column="habitat")
    diet = models.CharField(max_length=50, blank=True, null=True, db_column="diet")
    features = models.TextField(blank=True, null=True, db_column="features")
    care_conditions = models.TextField(blank=True, null=True, db_column="care_conditions")
    reproduction = models.TextField(blank=True, null=True, db_column="reproduction")
    image = models.TextField(blank=True, null=True, db_column="image")
    description = models.TextField(blank=True, null=True, db_column="description")
    animal_idAni = models.ForeignKey(Animal_main, on_delete=models.CASCADE, related_name="sorts", db_column='id_anim')


    class Meta:
        managed = False
        db_table = 'animals_animal'
