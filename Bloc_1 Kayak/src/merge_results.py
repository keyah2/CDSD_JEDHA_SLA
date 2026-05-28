from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def main() -> None:
    weather_path = DATA_DIR / "weather.csv"
    hotels_path = DATA_DIR / "hotels_multi_cities.csv"

    df_weather = pd.read_csv(weather_path)
    df_hotels = pd.read_csv(hotels_path)

    # On garde seulement les villes du top réellement scrapé
    cities_in_hotels = set(df_hotels["city"].dropna().unique())
    df_weather_top = df_weather[df_weather["city"].isin(cities_in_hotels)].copy()

    df_final = df_hotels.merge(
        df_weather_top,
        on="city",
        how="left"
    )

    output_path = DATA_DIR / "final_kayak_results.csv"
    df_final.to_csv(output_path, index=False, encoding="utf-8")

    print(f"[EXPORT] saved -> {output_path}")
    print(df_final.head())
    print("\nshape:", df_final.shape)
    print("\ncity counts:")
    print(df_final["city"].value_counts())


if __name__ == "__main__":
    main()