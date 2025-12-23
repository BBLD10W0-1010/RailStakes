import requests
import xml.etree.ElementTree as ET


class AltaApiClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/") + "/"
        self.api_key = api_key

    def calc(self, params: dict) -> dict:
        # Альта обычно отдаёт XML, удобнее сразу просить calc.xml
        params = {**params, "type": "calc", "api_key": self.api_key, "page": "calc.xml"}

        r = requests.get(self.base_url, params=params, timeout=30)
        r.raise_for_status()
        xml_text = r.text

        parsed = self._parse_calc_xml(xml_text)
        # raw_xml оставляем для дебага (но ключ потом будем вырезать)
        parsed["raw_xml"] = xml_text
        return parsed

    @staticmethod
    def _parse_calc_xml(xml_text: str) -> dict:
        root = ET.fromstring(xml_text)

        def get_tag(tag: str):
            el = root.find(f".//{tag}")
            if el is None:
                return None
            return {
                "value": el.attrib.get("value"),
                "currency": el.attrib.get("currency"),
                "unit": el.attrib.get("unit"),
            }

        status_el = root.find(".//status")
        status = status_el.text.strip() if status_el is not None and status_el.text else ""

        return {
            "status": status,
            "total_all": get_tag("total_all"),
            "tonna_all": get_tag("tonna_all"),
            "total_all_nalog": get_tag("total_all_nalog"),
            "guard_all": get_tag("guard_all"),
            "delivery_time": get_tag("delivery_time"),
        }
