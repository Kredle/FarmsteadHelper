from django.db import models

class Animal_main(models.Model):
    idAni = models.AutoField(primary_key=True, db_column='idani')
    Name = models.CharField(max_length=150, null=True, blank=True, db_column='name')
    Image = models.TextField(null=True, blank=True, db_column='image')
    
    class Meta:
        managed = False
        db_table = 'animals_animal_main'

class Animal(models.Model):
    id = models.AutoField(primary_key=True)
    scientific_name = models.CharField(max_length=150)
    common_name = models.CharField(max_length=100, blank=True, null=True)
    class_field = models.CharField(db_column='class', max_length=50, blank=True, null=True) 
    genus = models.CharField(max_length=100, blank=True, null=True)
    family = models.CharField(max_length=100, blank=True, null=True)
    size = models.CharField(max_length=100, blank=True, null=True)
    weight = models.CharField(max_length=50, blank=True, null=True)
    lifespan = models.CharField(max_length=50, blank=True, null=True)
    habitat = models.TextField(blank=True, null=True)
    diet = models.CharField(max_length=50, blank=True, null=True)
    features = models.TextField(blank=True, null=True)
    care_conditions = models.TextField(blank=True, null=True)
    reproduction = models.TextField(blank=True, null=True)
    usage = models.TextField(blank=True, null=True, db_column="application")
    image = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    animal_idAni = models.ForeignKey(Animal_main, on_delete=models.CASCADE, related_name="sorts", db_column='id_anim')


    class Meta:
        managed = False
        db_table = 'animals_animal'