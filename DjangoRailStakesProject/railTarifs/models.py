from django.db import models

# Create your models here.

class Station(models.Model):
    code = models.CharField("Код станции", max_length=20, unique=True)
    name = models.CharField("Название", max_length=255)

    class Meta:
        verbose_name = "Станция"
        verbose_name_plural = "Станции"
        ordering = ["name"]

    def get_name(self):
        return self.name
    def get_code(self):
        return self.code
    
class Cargo(models.Model):
    codeETG = models.CharField("Код груза (ЕТСНГ)", max_length=20, unique=True)
    codeGNG = models.CharField("Код груза (ГНГ)", max_length=20, null=True, blank=True)
    name = models.CharField("Наименование груза", max_length=255)

    class Meta:
        verbose_name = "Груз"
        verbose_name_plural = "Грузы"
        ordering = ["name"]

    def get_name(self):
        return self.name
    def get_codeETG(self):
        return self.codeETG
    def get_codeGNG(self):
        return self.codeGNG

class WagonType(models.Model):
    code = models.CharField("Код типа вагона", max_length=20, unique=True)
    name = models.CharField("Тип вагона", max_length=120)
    capacity_tons = models.DecimalField(
        "Грузоподъемность, т",
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Например: 68.00",
    )

    class Meta:
        verbose_name = "Тип вагона"
        verbose_name_plural = "Типы вагонов"
        ordering = ["name"]

    def get_name(self):
        return self.name
    def get_code(self):
        return self.code
    def get_capacity_tons(self):
        return self.capacity_tons
