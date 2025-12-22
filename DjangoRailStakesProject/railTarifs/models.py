from django.db import models


class Station(models.Model):
    code = models.CharField("Код станции", max_length=20, unique=True)
    name = models.CharField("Название", max_length=255)

    class Meta:
        verbose_name = "Станция"
        verbose_name_plural = "Станции"
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


class Cargo(models.Model):
    etsng_code = models.CharField("Код груза (ЕТСНГ)", max_length=20, unique=True)
    gng_code = models.CharField("Код груза (ГНГ)", max_length=20, null=True, blank=True)
    name = models.CharField("Наименование груза", max_length=255)

    class Meta:
        verbose_name = "Груз"
        verbose_name_plural = "Грузы"
        ordering = ["name"]

    def __str__(self) -> str:
        if self.gng_code:
            return f"{self.name} (ЕТСНГ {self.etsng_code}, ГНГ {self.gng_code})"
        return f"{self.name} (ЕТСНГ {self.etsng_code})"


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

    def __str__(self) -> str:
        cap = f", {self.capacity_tons}т" if self.capacity_tons is not None else ""
        return f"{self.name} ({self.code}{cap})"
