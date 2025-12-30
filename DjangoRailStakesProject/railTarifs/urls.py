from django.urls import path
from . import views

app_name = "railTarifs"

urlpatterns = [
    path("", views.tariff_calc_page, name="tariff_calc"),
    path("autocomplete/stations/", views.station_autocomplete, name="station_autocomplete"),
    path("autocomplete/cargos/", views.cargo_autocomplete, name="cargo_autocomplete"),
    path("my/", views.my_calculations, name="my_calculations"),
]
