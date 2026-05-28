"""
Étape 4 — Scraping Booking.com via ScrapingBee.

Lit  : data/top_cities.csv
Écrit: data/raw_booking_html/<ville>.html

ScrapingBee simule un vrai navigateur (render_js + stealth_proxy) pour contourner
les protections anti-bot de Booking.com.  Pour chaque ville on teste jusqu'à
4 variantes d'URL et on conserve la première qui retourne des fiches hôtels.

La fonction fetch_html_scrapingbee ne lève jamais d'exception :
elle retourne (html, http_code, error_message) pour que le pipeline
puisse continuer même en cas d'erreur sur une ville.
"""

import os
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_HTML_DIR = DATA_DIR / "raw_booking_html"
RAW_HTML_DIR.mkdir(exist_ok=True)

# override=True force le rechargement même si la variable est déjà en mémoire
load_dotenv(BASE_DIR / ".env", override=True)
SCRAPINGBEE_API_KEY = os.getenv("SCRAPINGBEE_API_KEY")


def build_booking_url_variants(city: str) -> list[tuple[str, str]]:
    """Retourne 4 variantes d'URL Booking pour maximiser les chances de résultats."""
    city_simple = quote_plus(city)
    city_france = quote_plus(f"{city}, France")

    return [
        (
            "city_france",
            f"https://www.booking.com/searchresults.fr.html?ss={city_france}",
        ),
        (
            "city_full",
            "https://www.booking.com/searchresults.fr.html"
            f"?ss={city_simple}&lang=fr&group_adults=2&no_rooms=1&group_children=0",
        ),
        (
            "city_simple",
            f"https://www.booking.com/searchresults.fr.html?ss={city_simple}",
        ),
        (
            "city_france_full",
            "https://www.booking.com/searchresults.fr.html"
            f"?ss={city_france}&lang=fr&group_adults=2&no_rooms=1&group_children=0",
        ),
    ]


def fetch_html_scrapingbee(target_url: str) -> tuple[str | None, int, str]:
    """
    Appelle ScrapingBee pour récupérer le HTML d'une URL Booking.
    Retourne (html, http_code, error_message).
    Ne lève jamais d'exception — les erreurs sont retournées dans le tuple.
    """
    if not SCRAPINGBEE_API_KEY:
        return None, 0, "SCRAPINGBEE_API_KEY manquante dans .env"

    api_url = "https://app.scrapingbee.com/api/v1/"
    params = {
        "api_key": SCRAPINGBEE_API_KEY,
        "url": target_url,
        "stealth_proxy": "true",   # proxy furtif anti-détection
        "country_code": "fr",      # IP française
        "render_js": "true",       # nécessaire pour Booking (contenu JS)
        "block_resources": "false",
    }

    try:
        resp = requests.get(api_url, params=params, timeout=90)
        if resp.status_code == 200:
            return resp.text, 200, ""
        return None, resp.status_code, resp.text[:300]
    except Exception as e:
        return None, 0, str(e)


def html_has_property_cards(html: str) -> tuple[bool, int]:
    """Vérifie si le HTML contient des fiches hôtels Booking."""
    count = html.count('data-testid="property-card"')
    return count > 0, count


def city_to_filename(city: str) -> str:
    """Convertit un nom de ville en nom de fichier sécurisé."""
    safe = (
        city.lower()
        .replace(" ", "_")
        .replace("é", "e").replace("è", "e").replace("ê", "e")
        .replace("à", "a").replace("ù", "u").replace("î", "i")
        .replace("ï", "i").replace("ô", "o").replace("ç", "c")
        .replace("'", "").replace("-", "_")
    )
    return f"booking_{safe}.html"


def fetch_and_save_city(city: str) -> bool:
    """
    Tente de scraper une ville.
    Retourne True si au moins une variante a renvoyé des fiches hôtels.
    """
    variants = build_booking_url_variants(city)

    for label, url in variants:
        print(f"  [TRY] variant={label}")
        html, code, err = fetch_html_scrapingbee(url)

        if code in (401, 403):
            # Clé invalide ou quota dépassé — inutile de continuer
            print(f"  [SCRAPINGBEE] KO (HTTP {code}) — {err}")
            print("  [ABORT] Clé invalide, arrêt du scraping.")
            return False

        if html is None:
            print(f"  [SCRAPINGBEE] KO (HTTP {code}) — {err}")
            continue

        ok, count = html_has_property_cards(html)
        print(f"  [SCRAPINGBEE] OK (HTTP {code}) | property_cards={count}")

        if ok:
            output_path = RAW_HTML_DIR / city_to_filename(city)
            output_path.write_text(html, encoding="utf-8")
            print(f"  [EXPORT] saved -> {output_path}")
            return True

        print(f"  [SKIP] variant={label} — aucune fiche hôtel")

    print(f"  [KO] Aucune variante valide pour {city}")
    return False


def main() -> None:
    top_cities_path = DATA_DIR / "top_cities.csv"
    df_top = pd.read_csv(top_cities_path)

    ok_count = 0

    for idx, row in df_top.iterrows():
        city = row["city"]
        print(f"\n[BOOKING] {idx + 1}/{len(df_top)} -> {city}")

        success = fetch_and_save_city(city)
        if success:
            ok_count += 1

    print(f"\n[RÉSULTAT] {ok_count}/{len(df_top)} villes scrapées avec succès")
    print(f"[HTML] dossier -> {RAW_HTML_DIR}")


if __name__ == "__main__":
    main()
