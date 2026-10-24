from collections import Counter


def _score(item):
    """Puntaje de momentum entre -100 y +100."""
    c1h = item["price_change_percentage_1h_in_currency"]
    c24 = item["price_change_percentage_24h"]
    c7d = item["price_change_percentage_7d_in_currency"]
    raw = 0.2 * c1h + 0.5 * c24 + 0.3 * c7d
    return max(-100.0, min(100.0, raw * 5))


def _trend_label(score):
    if score >= 20:
        return "ALCISTA_FUERTE"
    if score >= 5:
        return "ALCISTA"
    if score > -5:
        return "NEUTRAL"
    if score > -20:
        return "BAJISTA"
    return "BAJISTA_FUERTE"


def _volatility(item):
    """Rango del día (máximo - mínimo) relativo al precio, en %."""
    price = item["current_price"]
    if price <= 0:
        return 0.0
    return (item["high_24h"] - item["low_24h"]) / price * 100


def _risk_label(volatility):
    if volatility >= 10:
        return "ALTO"
    if volatility >= 4:
        return "MEDIO"
    return "BAJO"


def _cap_segments(items):
    """Divide en tercios por capitalización (clustering 1D)."""
    ordered = sorted(items, key=lambda r: r["market_cap"], reverse=True)
    n = len(ordered)
    segments = {}
    for idx, item in enumerate(ordered):
        ratio = idx / n if n else 0
        if ratio < 1 / 3:
            segments[item["id"]] = "large_cap"
        elif ratio < 2 / 3:
            segments[item["id"]] = "mid_cap"
        else:
            segments[item["id"]] = "small_cap"
    return segments


def classify(clean_records):
    if not clean_records:
        return [], {"total": 0}

    segments = _cap_segments(clean_records)
    results = []
    for item in clean_records:
        score = _score(item)
        vol = _volatility(item)
        results.append({
            "id": item["id"],
            "symbol": item["symbol"],
            "name": item["name"],
            "price_usd": round(item["current_price"], 6),
            "change_24h_pct": round(item["price_change_percentage_24h"], 2),
            "score": round(score, 2),
            "tendencia": _trend_label(score),
            "volatilidad_pct": round(vol, 2),
            "riesgo": _risk_label(vol),
            "segmento": segments[item["id"]],
        })

    results.sort(key=lambda r: r["score"], reverse=True)
    summary = {
        "total": len(results),
        "distribucion_tendencia": dict(Counter(r["tendencia"] for r in results)),
        "distribucion_riesgo": dict(Counter(r["riesgo"] for r in results)),
        "distribucion_segmento": dict(Counter(r["segmento"] for r in results)),
        "score_promedio": round(sum(r["score"] for r in results) / len(results), 2),
        "mejor": {"symbol": results[0]["symbol"], "score": results[0]["score"]},
        "peor": {"symbol": results[-1]["symbol"], "score": results[-1]["score"]},
    }
    return results, summary