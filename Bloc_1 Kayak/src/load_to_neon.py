"""
Étape 7 — Chargement du dataset final dans Neon PostgreSQL.

Lit  : data/final_kayak_results.csv
Écrit: table kayak_results dans la base Neon

La table est recréée à chaque exécution (DROP + CREATE) pour rester idempotente.
Les NaN pandas sont convertis en NULL PostgreSQL.
"""

import os
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# override=True force le rechargement même si la variable est déjà en mémoire
load_dotenv(BASE_DIR / ".env", override=True)
NEON_DATABASE_URL = os.getenv("NEON_DATABASE_URL")

EXPECTED_COLUMNS = [
    "city", "hotel_name", "hotel_score", "url", "description",
    "lat", "lon", "avg_temp_7d", "avg_pop_7d",
    "total_rain_7d", "avg_wind_7d", "weather_score",
]


def clean_value(value):
    """Convertit les NaN pandas en None (NULL PostgreSQL)."""
    if pd.isna(value):
        return None
    return value


def main() -> None:
    if not NEON_DATABASE_URL:
        print("[NEON] KO — NEON_DATABASE_URL manquante dans .env")
        return

    csv_path = DATA_DIR / "final_kayak_results.csv"
    if not csv_path.exists():
        print(f"[NEON] KO — Fichier introuvable : {csv_path}")
        return

    df = pd.read_csv(csv_path)

    missing = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    if missing:
        print(f"[NEON] KO — Colonnes manquantes : {missing}")
        return

    df = df[EXPECTED_COLUMNS].copy()
    rows = [tuple(clean_value(v) for v in row) for row in df.itertuples(index=False, name=None)]

    print(f"[NEON] Connexion à la base...")
    conn = psycopg2.connect(NEON_DATABASE_URL)
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            # Recréation de la table (idempotent)
            cur.execute("""
                DROP TABLE IF EXISTS kayak_results;

                CREATE TABLE kayak_results (
                    city            TEXT,
                    hotel_name      TEXT,
                    hotel_score     DOUBLE PRECISION,
                    url             TEXT,
                    description     TEXT,
                    lat             DOUBLE PRECISION,
                    lon             DOUBLE PRECISION,
                    avg_temp_7d     DOUBLE PRECISION,
                    avg_pop_7d      DOUBLE PRECISION,
                    total_rain_7d   DOUBLE PRECISION,
                    avg_wind_7d     DOUBLE PRECISION,
                    weather_score   DOUBLE PRECISION
                );
            """)

            execute_values(
                cur,
                """
                INSERT INTO kayak_results (
                    city, hotel_name, hotel_score, url, description,
                    lat, lon, avg_temp_7d, avg_pop_7d,
                    total_rain_7d, avg_wind_7d, weather_score
                ) VALUES %s
                """,
                rows,
                page_size=100,
            )

            conn.commit()

        print(f"[NEON] OK — {len(rows)} lignes insérées dans kayak_results")

    except Exception as e:
        conn.rollback()
        print(f"[NEON] KO — {e}")
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    main()
