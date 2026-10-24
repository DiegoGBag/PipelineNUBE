import json
from pipeline.cleaning import clean_payload
from pipeline.classifier import classify

datos = [
    {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin",
     "current_price": 83075, "market_cap": 1669934274886, "total_volume": 27796623802,
     "high_24h": 83249, "low_24h": 81155,
     "price_change_percentage_24h": 1.32733,
     "price_change_percentage_1h_in_currency": 0.1744,
     "price_change_percentage_7d_in_currency": -0.5564},
    {"id": "ethereum", "symbol": "eth", "name": "Ethereum",
     "current_price": 2456.29, "market_cap": 300112939171, "total_volume": 11547856921,
     "high_24h": 2471.63, "low_24h": 2374.52,
     "price_change_percentage_24h": 2.10107,
     "price_change_percentage_1h_in_currency": 0.305,
     "price_change_percentage_7d_in_currency": -2.206},
    {"id": "tether", "symbol": "usdt", "name": "Tether",
     "current_price": 0.999215, "market_cap": 183039136631, "total_volume": 51873608675,
     "high_24h": 0.999326, "low_24h": 0.999032,
     "price_change_percentage_24h": 0.00617,
     "price_change_percentage_1h_in_currency": 0.009,
     "price_change_percentage_7d_in_currency": -0.0162},
]

limpios, reporte_limpieza = clean_payload(datos)
resultados, resumen = classify(limpios)

print(json.dumps({"limpieza": reporte_limpieza, "resumen": resumen, "resultados": resultados},
                 indent=2, ensure_ascii=False))