import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from railTarifs.models import Station, Cargo, WagonType, Country


def split_name_code(raw: str):
    raw = (raw or "").strip()
    if "-" not in raw:
        return raw, ""
    name, code = raw.rsplit("-", 1)
    return name.strip(), code.strip()


class Command(BaseCommand):
    help = "Load reference data (stations, cargo, wagons, countries) from json files."

    def add_arguments(self, parser):
        parser.add_argument("--stations", default="stations.json")
        parser.add_argument("--cargo", default="cargo-types.json")
        parser.add_argument("--wagons", default="wagons (1).json")
        parser.add_argument("--countries", default="states.json")

    @transaction.atomic
    def handle(self, *args, **opts):
        base = Path.cwd()

        self._load_stations(base / opts["stations"])
        self._load_cargo(base / opts["cargo"])
        self._load_wagons(base / opts["wagons"])
        self._load_countries(base / opts["countries"])

        self.stdout.write(self.style.SUCCESS("✅ Reference data loaded."))

    def _read_list(self, path: Path):
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data = list(data.values())
        return data

    def _load_stations(self, path: Path):
        data = self._read_list(path)
        to_create = []
        for item in data:
            name, code = split_name_code(item.get("name"))
            if not code:
                continue
            to_create.append(Station(code=code, name=name))

        Station.objects.bulk_create(to_create, ignore_conflicts=True, batch_size=5000)
        self.stdout.write(f"Stations loaded: +{len(to_create)}")

    def _load_cargo(self, path: Path):
        data = self._read_list(path)
        to_create = []
        for item in data:
            name, code = split_name_code(item.get("name"))
            if not code:
                continue

            to_create.append(Cargo(codeETG=code, codeGNG=None, name=name))

        Cargo.objects.bulk_create(to_create, ignore_conflicts=True, batch_size=5000)
        self.stdout.write(f"Cargo loaded: +{len(to_create)}")

    def _load_wagons(self, path: Path):
        data = self._read_list(path)
        to_create = []
        for item in data:
            name, code = split_name_code(item.get("name"))
            if not code:
                continue
            to_create.append(WagonType(code=code, name=name))

        WagonType.objects.bulk_create(to_create, ignore_conflicts=True, batch_size=5000)
        self.stdout.write(f"Wagon types loaded: +{len(to_create)}")

    def _load_countries(self, path: Path):
        data = self._read_list(path)
        to_create = []
        for item in data:
            name, code = split_name_code(item.get("name"))
            if not code:
                continue
            to_create.append(Country(code=code, name=name))

        Country.objects.bulk_create(to_create, ignore_conflicts=True, batch_size=5000)
        self.stdout.write(f"Countries loaded: +{len(to_create)}")
