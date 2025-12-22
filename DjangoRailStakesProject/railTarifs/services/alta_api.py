from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Dict, Any
import xml.etree.ElementTree as ET

import requests


@dataclass
class AltaCalcResponse:
    ok: bool
    total_price: Optional[Decimal] = None
    currency: str = "RUB"
    error_text: str = ""
    raw_xml: str = ""


class AltaApiClient:
    def __init__(self, base_url: str, api_key: str, timeout: int = 20):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def calc(self, params: Dict[str, Any]) -> AltaCalcResponse:
        if not self.api_key:
            return AltaCalcResponse(ok=False, error_text="ALTA_API_KEY не задан в .env")

        full_params = {"type": "calc", "api_key": self.api_key}
        full_params.update(params)

        r = requests.get(self.base_url + "/", params=full_params, timeout=self.timeout)
        raw_xml = r.text

        if r.status_code != 200:
            return AltaCalcResponse(ok=False, error_text=f"HTTP {r.status_code}", raw_xml=raw_xml)

        # Ответ у Альта-Софт XML. Разбор сделаем максимально аккуратным: ищем ошибки и сумму.
        try:
            root = ET.fromstring(raw_xml)
        except ET.ParseError:
            return AltaCalcResponse(ok=False, error_text="Не удалось разобрать XML ответа", raw_xml=raw_xml)

        # Попытка найти текст ошибки (в разных ответах теги могут отличаться)
        text_all = " ".join(root.itertext()).strip().lower()
        if "error" in text_all or "ошиб" in text_all:
            return AltaCalcResponse(ok=False, error_text="API вернуло ошибку (см. raw_xml)", raw_xml=raw_xml)

        # Универсальный поиск числа "итого"/"total" — без гарантий, но рабочая база.
        # Когда увидим реальный XML — подстроим точный путь.
        total = None
        for node in root.iter():
            tag = node.tag.lower()
            if any(k in tag for k in ("total", "itogo", "sum", "price", "стоим", "итог")):
                if node.text:
                    s = node.text.strip().replace(",", ".")
                    try:
                        total = Decimal(s)
                        break
                    except Exception:
                        pass

        return AltaCalcResponse(ok=True, total_price=total, raw_xml=raw_xml)
