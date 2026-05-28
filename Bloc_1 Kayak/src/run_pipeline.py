"""
Orchestrateur du pipeline Kayak — exécute les 8 étapes dans l'ordre.

Usage :
    python src/run_pipeline.py              # pipeline complet
    python src/run_pipeline.py --from 4    # reprendre à partir de l'étape 4

Étapes :
    1  geocode_cities   — Géocodage Nominatim (35 villes)
    2  weather          — Météo OpenWeather /forecast (35 villes)
    3  select_top_cities — Sélection Top 5 par score météo
    4  scrape_booking_raw — Scraping Booking via ScrapingBee (5 villes)
    5  parse_booking    — Parsing HTML → CSV hôtels
    6  merge_results    — Fusion météo + hôtels
    7  load_to_neon     — Chargement PostgreSQL Neon
    8  generate_maps    — Génération cartes Folium HTML
"""

import argparse
import sys
import time
from pathlib import Path

# Ajout du dossier src au path pour les imports relatifs
SRC_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC_DIR))

import geocode_cities
import weather
import select_top_cities
import scrape_booking_raw
import parse_booking
import merge_results
import load_to_neon
import generate_maps

STEPS = [
    (1, "Géocodage Nominatim",       geocode_cities.main),
    (2, "Météo OpenWeather",         weather.main),
    (3, "Sélection Top 5",           select_top_cities.main),
    (4, "Scraping Booking",          scrape_booking_raw.main),
    (5, "Parsing HTML hôtels",       parse_booking.main),
    (6, "Fusion météo + hôtels",     merge_results.main),
    (7, "Chargement Neon PostgreSQL", load_to_neon.main),
    (8, "Génération cartes Folium",  generate_maps.main),
]


def run_step(step_num: int, label: str, fn) -> bool:
    """Exécute une étape du pipeline et retourne True si succès."""
    separator = "─" * 60
    print(f"\n{separator}")
    print(f"  ÉTAPE {step_num}/8 — {label}")
    print(separator)
    start = time.time()

    try:
        fn()
        elapsed = time.time() - start
        print(f"\n  ✓ Étape {step_num} terminée en {elapsed:.1f}s")
        return True
    except Exception as e:
        elapsed = time.time() - start
        print(f"\n  ✗ Étape {step_num} ÉCHOUÉE ({elapsed:.1f}s) : {e}")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Pipeline Kayak — orchestrateur")
    parser.add_argument(
        "--from",
        dest="start_from",
        type=int,
        default=1,
        metavar="N",
        help="Reprendre à partir de l'étape N (1-8, défaut: 1)",
    )
    parser.add_argument(
        "--only",
        dest="only",
        type=int,
        default=None,
        metavar="N",
        help="Exécuter uniquement l'étape N",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  PIPELINE KAYAK — JEDHA Bloc 1")
    print("=" * 60)

    steps_to_run = [
        (num, label, fn)
        for num, label, fn in STEPS
        if (args.only is None and num >= args.start_from)
        or (args.only is not None and num == args.only)
    ]

    if not steps_to_run:
        print(f"[ERREUR] Aucune étape valide (--from={args.start_from}, --only={args.only})")
        sys.exit(1)

    results = []
    pipeline_start = time.time()

    for num, label, fn in steps_to_run:
        success = run_step(num, label, fn)
        results.append((num, label, success))

        if not success:
            print(f"\n[PIPELINE] Arrêt à l'étape {num} suite à une erreur.")
            print("[PIPELINE] Corrigez l'erreur puis relancez avec : python src/run_pipeline.py --from", num)
            break

    total = time.time() - pipeline_start
    ok = sum(1 for _, _, s in results if s)
    total_run = len(results)

    print("\n" + "=" * 60)
    print(f"  RÉSUMÉ — {ok}/{total_run} étapes réussies — {total:.1f}s total")
    print("=" * 60)

    for num, label, success in results:
        icon = "✓" if success else "✗"
        print(f"  {icon}  Étape {num} — {label}")

    if ok == total_run == len(STEPS):
        print("\n  Pipeline complet ! Consultez maps/ pour les cartes.")

    sys.exit(0 if ok == total_run else 1)


if __name__ == "__main__":
    main()
