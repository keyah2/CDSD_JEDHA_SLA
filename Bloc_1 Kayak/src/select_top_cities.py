from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def main() -> None:
    weather_path = DATA_DIR / "weather.csv"
    df = pd.read_csv(weather_path)

    df_top = (
        df.sort_values(by="weather_score", ascending=False)
          .head(5)
          .copy()
    )

    output_path = DATA_DIR / "top_cities.csv"
    df_top.to_csv(output_path, index=False, encoding="utf-8")

    print(f"[EXPORT] saved -> {output_path}")
    print(df_top[["city", "weather_score"]])


if __name__ == "__main__":
    main()