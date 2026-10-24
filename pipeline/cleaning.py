import math
import re
import unicodedata
from statistics import median

NUMERIC_FIELDS = [
    "current_price", "market_cap", "total_volume",
    "price_change_percentage_1h_in_currency",
    "price_change_percentage_24h",
    "price_change_percentage_7d_in_currency",
    "high_24h", "low_24h",
]


def normalize_text(value):
    """Minúsculas, sin acentos, sin caracteres especiales."""
    if value is None:
        return ""
    text = unicodedata.normalize("NFKD", str(value))
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9\s\-]", "", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def to_float(value):
    """Convierte a float; devuelve None si no es un número válido."""
    if value is None or isinstance(value, bool):
        return None
    try:
        number = float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def clean_payload(raw_records):
    report = {
        "registros_recibidos": 0,
        "registros_descartados": 0,
        "valores_imputados": 0,
        "campos_no_numericos_corregidos": 0,
    }
    if not isinstance(raw_records, list):
        return [], report

    report["registros_recibidos"] = len(raw_records)

    # Pasada 1: normalizar y convertir
    staged = []
    for rec in raw_records:
        if not isinstance(rec, dict):
            report["registros_descartados"] += 1
            continue
        coin_id = normalize_text(rec.get("id"))
        if not coin_id:
            report["registros_descartados"] += 1
            continue
        item = {
            "id": coin_id,
            "symbol": normalize_text(rec.get("symbol")).upper(),
            "name": normalize_text(rec.get("name")).title(),
        }
        for field in NUMERIC_FIELDS:
            original = rec.get(field)
            parsed = to_float(original)
            if original is not None and parsed is None:
                report["campos_no_numericos_corregidos"] += 1
            item[field] = parsed
        if item["current_price"] is None or item["current_price"] <= 0:
            report["registros_descartados"] += 1
            continue
        staged.append(item)

    # Pasada 2: imputar faltantes con la mediana del lote
    medians = {}
    for field in NUMERIC_FIELDS:
        values = [r[field] for r in staged if r[field] is not None]
        medians[field] = median(values) if values else 0.0
    for item in staged:
        for field in NUMERIC_FIELDS:
            if item[field] is None:
                item[field] = medians[field]
                report["valores_imputados"] += 1

    return staged, report