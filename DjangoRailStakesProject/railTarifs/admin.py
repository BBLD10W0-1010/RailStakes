from django.contrib import admin
from .models import Station, Cargo, WagonType


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")


@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ("etsng_code", "gng_code", "name")
    search_fields = ("etsng_code", "gng_code", "name")
    list_filter = ("gng_code",)


@admin.register(WagonType)
class WagonTypeAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "capacity_tons")
    search_fields = ("code", "name")