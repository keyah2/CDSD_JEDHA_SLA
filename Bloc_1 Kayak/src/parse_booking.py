"""
Étape 5 — Parsing HTML des pages Booking.com.

Lit  : data/raw_booking_html/*.html
Écrit: data/hotels_multi_cities.csv

Pour chaque fichier HTML brut, on extrait via BeautifulSoup :
  - nom de l'hôtel
  - note client (0-10)
  - URL de la fiche
  - description de la chambre
Maximum 10 hôtels par ville, 50 au total.

Le nom de ville est déduit automatiquement du nom de fichier
(booking_aix_en_provence.html → Aix En Provence),
sauf surcharge dans FILENAME_TO_CITY pour les cas irréguliers.
"""

from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_HTML_DIR = DATA_DIR / "raw_booking_html"

# Surcharges manuelles pour les noms qui ne se reconstituent pas bien automatiquement
FILENAME_TO_CITY: dict[str, str] = {
    "booking_aix_en_provence.html": "Aix en Provence",
    "booking_avignon.html": "Avignon",
    "booking_bayonne.html": "Bayonne",
    "booking_bormes_les_mimosas.html": "Bormes les Mimosas",
    "booking_montauban.html": "Montauban",
    "booking_nimes.html": "Nimes",
    "booking_saintes_maries_de_la_mer.html": "Saintes Maries de la mer",
    "booking_aigues_mortes.html": "Aigues Mortes",
    "booking_gorges_du_verdon.html": "Gorges du Verdon",
    "booking_chateau_du_haut_koenigsbourg.html": "Chateau du Haut Koenigsbourg",
    "booking_mont_saint_michel.html": "Mont Saint Michel",
    "booking_st_malo.html": "St Malo",
    "booking_la_rochelle.html": "La Rochelle",
    "booking_strasbourg.html": "Strasbourg",
}


def filename_to_city(filename: str) -> str:
    """
    Déduit le nom de ville depuis le nom de fichier.
    Priorité : FILENAME_TO_CITY, sinon conversion automatique.
    """
    if filename in FILENAME_TO_CITY:
        return FILENAME_TO_CITY[filename]
    # Conversion automatique : booking_le_havre.html → Le Havre
    return (
        filename
        .replace("booking_", "")
        .replace(".html", "")
        .replace("_", " ")
        .title()
    )


def normalize_url(href: str) -> str:
    return urljoin("https://www.booking.com", href)


def extract_name(card) -> str | None:
    for selector in [
        '[data-testid="title"]',
        "div.f6431b446c",
        "div[data-testid='title'] div",
    ]:
        tag = card.select_one(selector)
        if tag:
            txt = tag.get_text(" ", strip=True)
            if txt and len(txt) > 2:
                return txt

    link = card.select_one('a[href*="/hotel/"]')
    if link:
        txt = link.get_text(" ", strip=True)
        if txt and len(txt) > 2:
            return txt

    return None


def extract_score(card) -> float | None:
    # Sélecteur principal data-testid
    tag = card.select_one('[data-testid="review-score"]')
    if tag:
        text = tag.get_text(" ", strip=True).replace(",", ".")
        for token in text.split():
            try:
                v = float(token)
                if 0 <= v <= 10:
                    return v
            except ValueError:
                pass

    # Sélecteurs alternatifs (aria-label)
    for tag in card.select('[data-testid="review-score"] div, [aria-label*="Note"], [aria-label*="Scored"]'):
        text = tag.get_text(" ", strip=True).replace(",", ".")
        for token in text.split():
            try:
                v = float(token)
                if 0 <= v <= 10:
                    return v
            except ValueError:
                pass

    return None


def extract_url(card) -> str | None:
    link = card.select_one('a[href*="/hotel/"]')
    if not link:
        return None
    href = link.get("href")
    return normalize_url(href) if href else None


def extract_description(card) -> str | None:
    for selector in [
        '[data-testid="property-card-unit-configuration"]',
        '[data-testid="property-card-unit-configuration-group"]',
        '[data-testid="property-card-unit-configuration-facilities"]',
        "div.abf093bdfe",
        "div.c624d7469d",
    ]:
        tag = card.select_one(selector)
        if tag:
            txt = tag.get_text(" ", strip=True)
            if txt and len(txt) > 10:
                return txt

    return None


def parse_hotels(html: str, city: str, max_hotels: int = 10) -> list[dict]:
    """Extrait jusqu'à max_hotels hôtels d'une page Booking."""
    soup = BeautifulSoup(html, "lxml")
    cards = soup.select('div[data-testid="property-card"]')
    print(f"  [PARSE] city={city} property_cards_found={len(cards)}")

    rows = []
    seen_urls: set[str] = set()

    for card in cards:
        name = extract_name(card)
        url = extract_url(card)

        if not name or not url:
            continue
        if url in seen_urls:
            continue
        seen_urls.add(url)

        rows.append({
            "city": city,
            "hotel_name": name,
            "hotel_score": extract_score(card),
            "url": url,
            "description": extract_description(card),
        })

        if len(rows) >= max_hotels:
            break

    return rows


def main() -> None:
    html_files = sorted(RAW_HTML_DIR.glob("booking_*.html"))

    if not html_files:
        print(f"[ERREUR] Aucun fichier HTML trouvé dans {RAW_HTML_DIR}")
        return

    all_rows = []

    for path in html_files:
        city = filename_to_city(path.name)
        print(f"\n[FILE] {path.name} -> city={city}")

        html = path.read_text(encoding="utf-8", errors="ignore")
        rows = parse_hotels(html, city=city, max_hotels=10)

        print(f"  [RESULT] hotels_found={len(rows)}")
        all_rows.extend(rows)

    df = pd.DataFrame(all_rows)
    output_path = DATA_DIR / "hotels_multi_cities.csv"
    df.to_csv(output_path, index=False, encoding="utf-8")

    print(f"\n[EXPORT] saved -> {output_path}")
    print(f"[RÉSULTAT] {len(df)} hôtels extraits ({df['city'].nunique()} villes)")
    print(df.head())


if __name__ == "__main__":
    main()
