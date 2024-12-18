from django.db import models

class Animal(models.Model):
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
    usage = models.TextField(blank=True, null=True)
    image = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'animals' 
