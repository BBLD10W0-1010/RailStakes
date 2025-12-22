from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .forms import TariffCalcForm
from .services.alta_api import AltaApiClient


@login_required
def tariff_calc_page(request):
    result = None
    form = TariffCalcForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        cargo = form.cleaned_data["cargo"]
        fst = form.cleaned_data["from_station"].code
        tst = form.cleaned_data["to_station"].code

        # fre/frg: берём из Cargo
        fre = getattr(cargo, "etsng_code", None) or getattr(cargo, "codeETG", None)
        frg = getattr(cargo, "gng_code", None) or getattr(cargo, "codeGNG", None)

        params = {
            "fst": fst,
            "tst": tst,
            "fre": fre,
            "fstate": form.cleaned_data["fstate"],
            "tstate": form.cleaned_data["tstate"],
            "van": form.cleaned_data["wagon_type"].code,  # если в API это “van”
            "w": form.cleaned_data["weight_kg"],
            "gp": str(form.cleaned_data["capacity_tons"]),
            "owner": 1 if form.cleaned_data["owner"] else 0,
            "empt": 1 if form.cleaned_data["empt"] else 0,
            "return": 0,
            "num_vagons": 1,
        }
        if frg:
            params["frg"] = frg

        client = AltaApiClient(settings.ALTA_API_BASE_URL, settings.ALTA_API_KEY)
        result = client.calc(params)

    return render(request, "railTarifs/tariff_calc.html", {"form": form, "result": result})

from django.http import JsonResponse
from django.db.models import Q
from .models import Station, Cargo


@login_required
def station_autocomplete(request):
    q = (request.GET.get("q") or "").strip()
    qs = Station.objects.all()

    if q:
        qs = qs.filter(Q(code__icontains=q) | Q(name__icontains=q))

    qs = qs.order_by("name")[:20]
    return JsonResponse({"results": [{"id": s.id, "text": f"{s.name} ({s.code})"} for s in qs]})


@login_required
def cargo_autocomplete(request):
    q = (request.GET.get("q") or "").strip()
    qs = Cargo.objects.all()

    if q:
        qs = qs.filter(
            Q(name__icontains=q)
            | Q(etsng_code__icontains=q)
            | Q(gng_code__icontains=q)
        )

    qs = qs.order_by("name")[:20]
    results = []
    for c in qs:
        label = f"{c.name} (ЕТСНГ {c.etsng_code}"
        if c.gng_code:
            label += f", ГНГ {c.gng_code}"
        label += ")"
        results.append({"id": c.id, "text": label})

    return JsonResponse({"results": results})
