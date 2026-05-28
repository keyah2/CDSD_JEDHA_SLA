"""
Étape 2 — Récupération des données météo via OpenWeather /forecast.

Lit  : data/cities_geocoded.csv
Écrit: data/weather.csv

Chaque ville reçoit un weather_score calculé à partir de :
  - température moyenne
  - probabilité de pluie moyenne
  - cumul de pluie total
  - vitesse de vent moyenne
sur les 5 prochains jours (40 créneaux de 3 h).
"""

import os
from collections import defaultdict
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# override=True force le rechargement même si la variable est déjà en mémoire
load_dotenv(BASE_DIR / ".env", override=True)
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


def compute_weather_score(
    avg_temp: float,
    avg_pop: float,
    total_rain: float,
    avg_wind: float,
) -> float:
    """Formule de scoring météo /100 (température idéale = 24 °C)."""
    score = 100.0
    score -= abs(avg_temp - 24) * 2.0   # pénalité écart température
    score -= avg_pop * 30.0              # pénalité probabilité de pluie
    score -= total_rain * 1.5            # pénalité cumul de pluie
    score -= avg_wind * 0.8              # pénalité vent
    return round(score, 2)


def fetch_forecast(lat: float, lon: float) -> tuple[dict | None, str, int, str]:
    """
    Appelle /data/2.5/forecast (plan gratuit, 40 créneaux de 3 h sur 5 jours).
    Retourne (data_json, status, http_code, error_message).
    """
    if not OPENWEATHER_API_KEY:
        return None, "KO", 0, "OPENWEATHER_API_KEY manquante dans .env"

    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
        "cnt": 40,  # 40 créneaux × 3 h = 5 jours complets
    }

    try:
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code == 200:
            return resp.json(), "OK", 200, ""
        return None, "KO", resp.status_code, resp.text[:200]
    except Exception as e:
        return None, "KO", 0, str(e)


def summarize_city_weather(city: str, lat: float, lon: float) -> dict | None:
    """
    Agrège les 40 créneaux de 3 h par jour, puis calcule les indicateurs
    moyens sur les 5 jours et le weather_score.
    """
    data, status, code, err = fetch_forecast(lat, lon)
    print(f"[OPENWEATHER] {city} -> {status} (HTTP {code})" + (f" | {err}" if err else ""))

    if data is None:
        return None

    # Regroupement par date (clé = "YYYY-MM-DD")
    daily: dict[str, list] = defaultdict(list)
    for slot in data.get("list", []):
        date_key = slot["dt_txt"][:10]
        daily[date_key].append(slot)

    if not daily:
        print(f"[OPENWEATHER] {city} -> KO (aucun créneau reçu)")
        return None

    temps, pops, rains, winds = [], [], [], []

    for slots in daily.values():
        temps.append(sum(s["main"]["temp"] for s in slots) / len(slots))
        pops.append(sum(s.get("pop", 0) for s in slots) / len(slots))
        rains.append(sum(s.get("rain", {}).get("3h", 0) for s in slots))
        winds.append(sum(s["wind"]["speed"] for s in slots) / len(slots))

    avg_temp = sum(temps) / len(temps)
    avg_pop = sum(pops) / len(pops)
    total_rain = sum(rains)
    avg_wind = sum(winds) / len(winds)

    return {
        "city": city,
        "lat": lat,
        "lon": lon,
        "avg_temp_7d": round(avg_temp, 2),
        "avg_pop_7d": round(avg_pop, 4),
        "total_rain_7d": round(total_rain, 2),
        "avg_wind_7d": round(avg_wind, 2),
        "weather_score": compute_weather_score(avg_temp, avg_pop, total_rain, avg_wind),
    }


def main() -> None:
    cities_path = DATA_DIR / "cities_geocoded.csv"
    df_cities = pd.read_csv(cities_path)

    rows = []
    ok_count = 0

    for idx, row in df_cities.iterrows():
        city = row["city"]
        lat = float(row["lat"])
        lon = float(row["lon"])

        print(f"\n[OPENWEATHER] {idx + 1}/{len(df_cities)} -> {city}")
        result = summarize_city_weather(city, lat, lon)

        if result:
            rows.append(result)
            ok_count += 1
        else:
            rows.append({"city": city, "lat": lat, "lon": lon,
                         "avg_temp_7d": None, "avg_pop_7d": None,
                         "total_rain_7d": None, "avg_wind_7d": None,
                         "weather_score": None})

    df_weather = pd.DataFrame(rows)
    output_path = DATA_DIR / "weather.csv"
    df_weather.to_csv(output_path, index=False, encoding="utf-8")

    print(f"\n[EXPORT] saved -> {output_path}")
    print(f"[RÉSULTAT] {ok_count}/{len(df_cities)} villes avec données météo")
    print(df_weather[["city", "avg_temp_7d", "weather_score"]].head(10))


if __name__ == "__main__":
    main()
