import os
from datetime import datetime, timezone

import requests
from flask import Flask, jsonify, request

from pipeline.classifier import classify
from pipeline.cleaning import clean_payload

app = Flask(__name__)
COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"


def run_pipeline(raw_records, source):
    clean, cleaning_report = clean_payload(raw_records)
    results, summary = classify(clean)
    return {
        "pipeline": "crypto-mining-pipeline",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "fuente": source,
        "limpieza": cleaning_report,
        "resumen": summary,
        "resultados": results,
    }


def fetch_coingecko(limit=25):
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": limit,
        "page": 1,
        "price_change_percentage": "1h,24h,7d",
    }
    headers = {"Accept": "application/json", "User-Agent": "crypto-pipeline/1.0"}
    key = os.environ.get("COINGECKO_API_KEY")  # opcional
    if key:
        headers["x-cg-demo-api-key"] = key
    resp = requests.get(COINGECKO_URL, params=params, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()


@app.get("/")
@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "servicio": "crypto-mining-pipeline"})


@app.post("/api/analyze")
def analyze():
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "Se esperaba un JSON en el cuerpo"}), 400
    if isinstance(payload, dict):
        payload = payload.get("data", [])
    if not isinstance(payload, list):
        return jsonify({"error": "El payload debe ser una lista"}), 400
    return jsonify(run_pipeline(payload, source="payload_cliente"))


@app.get("/api/pipeline")
def pipeline():
    try:
        limit = max(1, min(int(request.args.get("limit", 25)), 100))
    except ValueError:
        limit = 25
    try:
        raw = fetch_coingecko(limit)
    except requests.RequestException as exc:
        return jsonify({"error": "No se pudo consultar CoinGecko", "detalle": str(exc)}), 502
    return jsonify(run_pipeline(raw, source="coingecko_live"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))