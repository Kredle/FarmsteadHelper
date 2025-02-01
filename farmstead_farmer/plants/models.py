from django.db import models

class Plant(models.Model):
    name = models.CharField(max_length=100)
    family = models.CharField(max_length=50, null=True, blank=True)
    type_of_life = models.CharField(max_length=20, null=True, blank=True)
    height = models.TextField()
    flower_color = models.CharField(max_length=100, null=True, blank=True)
    flowering_period = models.CharField(max_length=50, null=True, blank=True)
    conditions_of_care = models.TextField()
    growth_regions = models.CharField(max_length=200, null=True, blank=True)
    soil = models.CharField(max_length=100, null=True, blank=True)
    temperature = models.CharField(max_length=50, null=True, blank=True)
    recommended_humidity = models.CharField(max_length=50, null=True, blank=True)
    image = models.TextField()
    description = models.TextField()

    class Meta:
        managed = False
        db_table = 'plants' 

    def __str__(self):
        return self.name
