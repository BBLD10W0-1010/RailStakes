from django import forms
from .models import Station, Cargo, WagonType


class TariffCalcForm(forms.Form):
    cargo = forms.ModelChoiceField(
        label="Вид груза",
        queryset=Cargo.objects.all(),
        widget=forms.Select(attrs={"class": "form-select js-cargo"}),
    )
    from_station = forms.ModelChoiceField(
        label="Станция отправления",
        queryset=Station.objects.all(),
        widget=forms.Select(attrs={"class": "form-select js-station"}),
    )
    to_station = forms.ModelChoiceField(
        label="Станция назначения",
        queryset=Station.objects.all(),
        widget=forms.Select(attrs={"class": "form-select js-station"}),
    )

    fstate = forms.IntegerField(
        label="Страна отправления",
        initial=20,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    tstate = forms.IntegerField(
        label="Страна назначения",
        initial=20,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )

    wagon_type = forms.ModelChoiceField(
        label="Тип вагона",
        queryset=WagonType.objects.all(),
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    weight_kg = forms.IntegerField(
        label="Вес, кг",
        initial=60000,
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    capacity_tons = forms.DecimalField(
        label="Грузоподъемность, т",
        initial=66,
        min_value=0,
        decimal_places=2,
        max_digits=7,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )

    empt = forms.BooleanField(
        label="Порожняя отправка",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
    owner = forms.BooleanField(
        label="Собственный/арендованный",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("from_station") and cleaned.get("to_station"):
            if cleaned["from_station"] == cleaned["to_station"]:
                self.add_error("to_station", "Станция назначения должна отличаться от станции отправления.")
        return cleaned
