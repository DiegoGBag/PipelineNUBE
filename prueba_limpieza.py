from pipeline.cleaning import clean_payload

datos = [
    {"id": "Dogé Coin!!", "symbol": "doge#", "name": " Dogé  Coin ",
     "current_price": "0.15", "market_cap": "N/A", "high_24h": 0.16},
    {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin",
     "current_price": 67000, "market_cap": 1.3e12, "high_24h": 68000},
    {"id": "", "current_price": 10},
]

limpios, reporte = clean_payload(datos)
print(limpios)
print(reporte)