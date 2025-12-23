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
    name = models.CharField("Наименование груза", max_length=600)

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
    name = models.CharField("Тип вагона", max_length=600)
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


from django.conf import settings
from django.db import models


class TariffQuery(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tariff_queries",
        verbose_name="Пользователь",
    )

    from_station = models.ForeignKey(
        "Station",
        on_delete=models.PROTECT,
        related_name="queries_from",
        verbose_name="Станция отправления",
    )
    to_station = models.ForeignKey(
        "Station",
        on_delete=models.PROTECT,
        related_name="queries_to",
        verbose_name="Станция назначения",
    )

    cargo = models.ForeignKey("Cargo", on_delete=models.PROTECT, verbose_name="Груз")
    wagon_type = models.ForeignKey("WagonType", on_delete=models.PROTECT, verbose_name="Тип вагона")

    fstate = models.PositiveSmallIntegerField("Код страны отправления", default=20)
    tstate = models.PositiveSmallIntegerField("Код страны назначения", default=20)

    modular = models.BooleanField("Сборная отправка (modular)", default=False)
    empt = models.BooleanField("Порожняя отправка (empt)", default=False)
    owner = models.BooleanField("Собственный/арендованный (owner)", default=False)
    return_calc = models.BooleanField("Рассчитывать возврат (return)", default=False)
    return_station = models.ForeignKey(
        "Station",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="queries_return",
        verbose_name="Станция возврата (return_st)",
    )

    is_speed = models.BooleanField("Большая скорость (is_speed)", default=True)
    is_cont_train = models.BooleanField("Контейнерный поезд (is_cont_train)", default=True)
    route = models.BooleanField("Нитка маршрута (route)", default=True)

    calc_date = models.DateField("Дата расчёта (calc_date)", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Запрос тарифа"
        verbose_name_plural = "Запросы тарифов"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.from_station.code}->{self.to_station.code} / {self.created_at:%Y-%m-%d %H:%M}"


class TariffWagon(models.Model):
    query = models.ForeignKey(
        TariffQuery,
        on_delete=models.CASCADE,
        related_name="wagons",
        verbose_name="Запрос",
    )
    index = models.PositiveSmallIntegerField("№ вагона (1..N)")
    weight_kg = models.PositiveIntegerField("Вес, кг (w/wN)")
    capacity_tons = models.DecimalField("Г/п, т (gp/gpN)", max_digits=7, decimal_places=2)

    class Meta:
        verbose_name = "Вагон в отправке"
        verbose_name_plural = "Вагоны в отправке"
        ordering = ["index"]
        constraints = [
            models.UniqueConstraint(fields=["query", "index"], name="uniq_wagon_index_per_query")
        ]

    def __str__(self) -> str:
        return f"Вагон {self.index}: {self.weight_kg} кг / {self.capacity_tons} т"


class TariffResult(models.Model):
    query = models.OneToOneField(
        TariffQuery,
        on_delete=models.CASCADE,
        related_name="result",
        verbose_name="Запрос",
    )
    ok = models.BooleanField("Успешно", default=False)
    total_price = models.DecimalField("Итоговая ставка", max_digits=14, decimal_places=2, null=True, blank=True)
    currency = models.CharField("Валюта", max_length=10, blank=True, default="RUB")

    raw_xml = models.TextField("Ответ API (XML)", blank=True)
    error_text = models.TextField("Ошибка", blank=True)

    calculated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Результат расчёта"
        verbose_name_plural = "Результаты расчётов"
        ordering = ["-calculated_at"]

class Country(models.Model):
    code = models.CharField("Код страны", max_length=5, unique=True)  # "20"
    name = models.CharField("Страна", max_length=120)

    class Meta:
        verbose_name = "Страна"
        verbose_name_plural = "Страны"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"