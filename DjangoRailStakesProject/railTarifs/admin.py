from django.contrib import admin
from .models import Station, Cargo, WagonType, TariffQuery, TariffWagon, TariffResult


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")


@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ("etsng_code", "gng_code", "name")
    search_fields = ("etsng_code", "gng_code", "name")


@admin.register(WagonType)
class WagonTypeAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "capacity_tons")
    search_fields = ("code", "name")


class TariffWagonInline(admin.TabularInline):
    model = TariffWagon
    extra = 1


@admin.register(TariffQuery)
class TariffQueryAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "from_station", "to_station", "cargo", "wagon_type", "empt", "created_at")
    search_fields = ("from_station__code", "to_station__code", "cargo__name", "cargo__etsng_code")
    list_filter = ("empt", "owner", "modular", "created_at")
    inlines = [TariffWagonInline]


@admin.register(TariffResult)
class TariffResultAdmin(admin.ModelAdmin):
    list_display = ("query", "ok", "total_price", "currency", "calculated_at")
    list_filter = ("ok", "calculated_at")
