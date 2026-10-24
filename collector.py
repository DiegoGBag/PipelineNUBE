import argparse
import json
import time
from datetime import datetime, timezone

import requests

COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"


def extract(limit):
    """Etapa 1: extracción en vivo desde CoinGecko."""
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": limit,
        "page": 1,
        "price_change_percentage": "1h,24h,7d",
    }
    resp = requests.get(COINGECKO_URL, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def send(service_url, raw):
    """Etapa 2: enviar el payload crudo al microservicio."""
    resp = requests.post(f"{service_url.rstrip('/')}/api/analyze", json=raw, timeout=30)
    resp.raise_for_status()
    return resp.json()


def run_once(args):
    raw = extract(args.limit)
    print(f"[{datetime.now(timezone.utc).isoformat()}] Extraídos {len(raw)} registros")
    result = send(args.service_url, raw)
    with open(args.output, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(result, ensure_ascii=False) + "\n")  # un JSON por línea
    print(json.dumps(result["resumen"], indent=2, ensure_ascii=False))
    print(f"Log agregado a {args.output}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--service-url", default="http://localhost:5000")
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--output", default="log_resultados.jsonl")
    parser.add_argument("--loop", type=int, default=0, help="Repetir cada N segundos")
    args = parser.parse_args()

    while True:
        try:
            run_once(args)
        except requests.RequestException as exc:
            print(f"Error de red: {exc}")
        if args.loop <= 0:
            break
        time.sleep(args.loop)


if __name__ == "__main__":
    main()