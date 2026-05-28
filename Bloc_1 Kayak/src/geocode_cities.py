"""
Étape 1 — Géocodage des villes via Nominatim (OpenStreetMap).

Écrit: data/cities_geocoded.csv

Nominatim est gratuit et sans clé API.
Contrainte : 1 requête/seconde maximum → time.sleep(1.1) entre chaque appel.
"""

import time
from pathlib import Path

import pandas as pd
import requests

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

CITIES = [
    "Mont Saint Michel",
    "St Malo",
    "Bayeux",
    "Le Havre",
    "Rouen",
    "Paris",
    "Amiens",
    "Lille",
    "Strasbourg",
    "Chateau du Haut Koenigsbourg",
    "Colmar",
    "Eguisheim",
    "Besancon",
    "Dijon",
    "Annecy",
    "Grenoble",
    "Lyon",
    "Gorges du Verdon",
    "Bormes les Mimosas",
    "Cassis",
    "Marseille",
    "Aix en Provence",
    "Avignon",
    "Uzes",
    "Nimes",
    "Aigues Mortes",
    "Saintes Maries de la mer",
    "Collioure",
    "Carcassonne",
    "Ariege",
    "Toulouse",
    "Montauban",
    "Biarritz",
    "Bayonne",
    "La Rochelle",
]

HEADERS = {"User-Agent": "KayakProjectJEDHA/1.0 (geocoding)"}


def geocode_city(city: str) -> tuple[dict, str, int, str]:
    """
    Géocode une ville via Nominatim.
    Retourne (result_dict, status, http_code, error_message).
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": f"{city}, France", "format": "jsonv2", "limit": 1}

    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=30)

        if resp.status_code != 200:
            return (
                {"city": city, "lat": None, "lon": None},
                "KO", resp.status_code, resp.text[:200],
            )

        results = resp.json()

        if not results:
            return (
                {"city": city, "lat": None, "lon": None},
                "KO", 200, "Aucun résultat retourné",
            )

        first = results[0]
        return (
            {"city": city, "lat": float(first["lat"]), "lon": float(first["lon"])},
            "OK", 200, "",
        )

    except Exception as e:
        return {"city": city, "lat": None, "lon": None}, "KO", 0, str(e)


def main() -> None:
    rows = []
    ok_count = 0

    for idx, city in enumerate(CITIES, start=1):
        row, status, code, err = geocode_city(city)
        rows.append(row)

        if status == "OK":
            ok_count += 1
            print(f"[NOMINATIM] {idx:02d}/{len(CITIES)} {city} -> OK (lat={row['lat']:.4f}, lon={row['lon']:.4f})")
        else:
            print(f"[NOMINATIM] {idx:02d}/{len(CITIES)} {city} -> KO (HTTP {code}) | {err}")

        time.sleep(1.1)  # respect limite 1 req/s de Nominatim

    df = pd.DataFrame(rows)
    df.insert(0, "id", range(1, len(df) + 1))

    output_path = DATA_DIR / "cities_geocoded.csv"
    df.to_csv(output_path, index=False, encoding="utf-8")

    print(f"\n[EXPORT] saved -> {output_path}")
    print(f"[RÉSULTAT] {ok_count}/{len(CITIES)} villes géocodées avec succès")
    print(df.head())


if __name__ == "__main__":
    main()
