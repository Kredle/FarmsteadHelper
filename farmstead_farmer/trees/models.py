from django.db import models


class Tree(models.Model):
    idTree = models.AutoField(primary_key=True, db_column='idtree')
    name = models.CharField(max_length=150, verbose_name="Назва", null=True, blank=True, db_column='Name')
    family = models.CharField(max_length=50, verbose_name="Родина", null=True, blank=True, db_column='Family')
    scope_of_bloom = models.CharField(max_length=50, verbose_name="Період цвітіння", null=True, blank=True)
    ripe_time = models.CharField(max_length=45, verbose_name="Час дозрівання", null=True, blank=True)
    image_tree = models.TextField(verbose_name="Зображення дерева", null=True, blank=True)
    compatible = models.TextField(verbose_name="Сумісність", null=True, blank=True)
    incompatible = models.TextField(verbose_name="Несумісність", null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'tree'

    def __str__(self):
        return self.name if self.name else f"Tree {self.id}"


class Sort(models.Model):
    idSort = models.AutoField(primary_key=True, db_column='idsort')
    sort = models.CharField(max_length=150, verbose_name="Сорт", null=True, blank=True)
    leaves = models.TextField(verbose_name="Листя", null=True, blank=True)
    ground_type = models.TextField(verbose_name="Тип ґрунту", null=True, blank=True)
    temperature_scope = models.TextField(verbose_name="Температурний діапазон", null=True, blank=True)
    usage = models.CharField(max_length=45, verbose_name="Використання", null=True, blank=True, db_column='Usage')
    discription = models.TextField(verbose_name="Опис", null=True, blank=True)
    image_fruit = models.TextField(verbose_name="Зображення плоду", null=True, blank=True)
    tree = models.ForeignKey(Tree, on_delete=models.CASCADE, related_name="sorts", verbose_name="Дерево", db_column='tree_idtree')

    class Meta:
        managed = False
        db_table = 'sorts'

    def __str__(self):
        return self.sort if self.sort else f"Sort {self.id}"


class Cutting(models.Model):
    idCutting = models.AutoField(primary_key=True, db_column='idcutting')
    cutting_time = models.TextField(verbose_name="Час обрізки", null=True, blank=True)
    cutting_discription = models.TextField(verbose_name="Опис обрізки", null=True, blank=True, db_column='Cutting discription')
    cutting_treatment = models.TextField(verbose_name="Лікування після обрізки", null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'cutting'

    def __str__(self):
        return f"Cutting {self.idCutting}"


class Disease(models.Model):
    idDiseases = models.AutoField(primary_key=True, db_column='iddiseases')
    disease_name = models.CharField(max_length=45, verbose_name="Назва хвороби", null=True, blank=True)
    disease_discription = models.TextField(verbose_name="Опис хвороби", null=True, blank=True)
    disease_treatment = models.TextField(verbose_name="Лікування хвороби", null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'diseases'

    def __str__(self):
        return self.disease_name if self.disease_name else f"Disease {self.idDiseases}"


class Fertilizer(models.Model):
    idFertilizer = models.AutoField(primary_key=True, db_column='idfertilizer')
    fertilizer = models.CharField(max_length=45, verbose_name="Добриво", null=True, blank=True)
    fertilizer_type = models.CharField(max_length=45, verbose_name="Тип добрива", null=True, blank=True)
    fertilizer_date = models.TextField(verbose_name="Дата внесення добрива", null=True, blank=True)
    application_method = models.CharField(max_length=45, verbose_name="Метод внесення", null=True, blank=True)
    quantity = models.TextField(verbose_name="Кількість", null=True, blank=True)
    fertilizer_discription = models.TextField(verbose_name="Опис добрива", null=True, blank=True, db_column='frtilizer_discription')

    class Meta:
        managed = False
        db_table = 'fertilizer'

    def __str__(self):
        return self.fertilizer if self.fertilizer else f"Fertilizer {self.idFertilizer}"


class Planting(models.Model):
    idPlanting = models.AutoField(primary_key=True, db_column='idplantting')
    plant_time = models.TextField(verbose_name="Час посадки", null=True, blank=True)
    planting_discription = models.TextField(verbose_name="Опис посадки", null=True, blank=True, db_column='plantting_discription')

    class Meta:
        managed = False
        db_table = 'planting'

    def __str__(self):
        return f"Planting {self.idPlanting}"
