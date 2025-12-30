from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib import messages
from .forms import TariffCalcForm
from .services.alta_api import AltaApiClient
from .models import TariffQuery, TariffResult, TariffWagon
from django.db import transaction

@login_required
def tariff_calc_page(request):
    result = None
    form = TariffCalcForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        quota = getattr(request.user, "quota", None)
        if not quota:
            # на всякий пожарный (если сигнал не отработал)
            from .models import UserQuota
            quota = UserQuota.objects.create(user=request.user, total_limit=5)

        if quota.remaining() <= 0:
            messages.error(request, "Лимит запросов исчерпан. Обратитесь к администратору для увеличения лимита.")
            return render(request, "railTarifs/tariff_calc.html", {"form": form, "result": None})

        cargo = form.cleaned_data["cargo"]
        fst = form.cleaned_data["from_station"].code
        tst = form.cleaned_data["to_station"].code

        fre = getattr(cargo, "etsng_code", None) or getattr(cargo, "codeETG", None)
        frg = getattr(cargo, "gng_code", None) or getattr(cargo, "codeGNG", None)

        params = {
            "fst": fst,
            "tst": tst,
            "fre": fre,
            "fstate": form.cleaned_data["fstate"],
            "tstate": form.cleaned_data["tstate"],
            "van": form.cleaned_data["wagon_type"].code,
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

        with transaction.atomic():
            qobj = TariffQuery.objects.create(
                user=request.user,
                from_station=form.cleaned_data["from_station"],
                to_station=form.cleaned_data["to_station"],
                cargo=cargo,
                wagon_type=form.cleaned_data["wagon_type"],
                fstate=form.cleaned_data["fstate"],
                tstate=form.cleaned_data["tstate"],
                empt=form.cleaned_data["empt"],
                owner=form.cleaned_data["owner"],
                return_calc=False,
            )
            TariffWagon.objects.create(
                query=qobj,
                index=1,
                weight_kg=form.cleaned_data["weight_kg"],
                capacity_tons=form.cleaned_data["capacity_tons"],
            )

            api_result = client.calc(params)

            # сохраним сырьё/итог в БД
            ok = (getattr(api_result, "status", None) == "ok") or (isinstance(api_result, dict) and api_result.get("status") == "ok")

            total_price = None
            currency = "RUB"
            raw_xml = getattr(api_result, "raw_xml", "") if not isinstance(api_result, dict) else api_result.get("raw_xml", "")

            total_all = getattr(api_result, "total_all", None) if not isinstance(api_result, dict) else api_result.get("total_all")
            if total_all and getattr(total_all, "value", None):
                total_price = total_all.value
                currency = getattr(total_all, "currency", currency)

            TariffResult.objects.create(
                query=qobj,
                ok=ok,
                total_price=total_price,
                currency=currency or "RUB",
                raw_xml=raw_xml or "",
                error_text="" if ok else "Ошибка расчёта",
            )

            quota.used += 1
            quota.save(update_fields=["used"])

        result = api_result
    quota_remaining = request.user.quota.remaining() if hasattr(request.user, "quota") else None   
    return render(request, "railTarifs/tariff_calc.html", {"form": form, "result": result, "quota_remaining": quota_remaining})

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
