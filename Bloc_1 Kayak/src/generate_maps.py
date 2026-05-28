"""
Étape 8 — Génération des cartes interactives Folium.

Lit  : data/top_cities.csv + data/final_kayak_results.csv
Écrit: maps/map_top_5_destinations.html
       maps/map_top_20_hotels.html

Les hôtels d'une même ville sont disposés en cercle autour du centre-ville
(décalage trigonométrique) pour éviter la superposition des marqueurs.
"""

import math
from pathlib import Path

import folium
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
MAPS_DIR = ROOT_DIR / "maps"
MAPS_DIR.mkdir(exist_ok=True)

# Couleurs par ville — s'adapte dynamiquement aux villes présentes dans les données
CITY_COLORS = {
    "Bayonne": "blue",
    "Aix en Provence": "green",
    "Montauban": "red",
    "Nimes": "purple",
    "Avignon": "orange",
    "Bormes les Mimosas": "darkblue",
    "Strasbourg": "cadetblue",
}
DEFAULT_COLOR = "gray"


def clean_text(x) -> str:
    if pd.isna(x):
        return ""
    return str(x).strip()


def shorten(text: str, max_len: int = 42) -> str:
    text = clean_text(text)
    return text if len(text) <= max_len else text[: max_len - 3] + "..."


def prepare_visual_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Décale légèrement les marqueurs d'hôtels d'une même ville en cercle
    pour qu'ils soient tous visibles sur la carte (évite la superposition).
    """
    parts = []

    for city, group in df.groupby("city", sort=False):
        g = group.copy().reset_index(drop=True)
        base_lat = float(g["lat"].iloc[0])
        base_lon = float(g["lon"].iloc[0])
        n = len(g)

        if n == 1:
            g.loc[0, "plot_lat"] = base_lat
            g.loc[0, "plot_lon"] = base_lon
        else:
            for i in range(n):
                angle = (2 * math.pi * i) / n
                radius = 0.025 + (0.004 * (i % 3))
                lat_offset = radius * math.sin(angle)
                lon_offset = (radius * math.cos(angle)) / max(math.cos(math.radians(base_lat)), 0.35)
                g.loc[i, "plot_lat"] = base_lat + lat_offset
                g.loc[i, "plot_lon"] = base_lon + lon_offset

        parts.append(g)

    return pd.concat(parts, ignore_index=True)


def add_map_title(m: folium.Map, title: str) -> None:
    m.get_root().html.add_child(folium.Element(
        f'<h3 align="center" style="font-size:20px; margin-top:8px;"><b>{title}</b></h3>'
    ))


def build_top5_map(df_top5: pd.DataFrame) -> None:
    """Carte avec un marqueur par ville + popup météo au clic."""
    m = folium.Map(
        location=[df_top5["lat"].mean(), df_top5["lon"].mean()],
        zoom_start=6,
        tiles="OpenStreetMap",
    )
    add_map_title(m, "Top 5 destinations kayak")

    bounds = []
    for _, row in df_top5.iterrows():
        bounds.append([row["lat"], row["lon"]])

        popup_html = (
            f"<b>Ville :</b> {row['city']}<br>"
            f"<b>Score météo :</b> {row['weather_score']:.2f}<br>"
            f"<b>Température moyenne :</b> {row['avg_temp_7d']:.1f} °C<br>"
            f"<b>Probabilité pluie :</b> {row['avg_pop_7d']:.2f}<br>"
            f"<b>Pluie totale :</b> {row['total_rain_7d']:.1f} mm<br>"
            f"<b>Vent moyen :</b> {row['avg_wind_7d']:.1f} m/s"
        )

        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=10,
            color="blue",
            fill=True,
            fill_color="blue",
            fill_opacity=0.75,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=row["city"],
        ).add_to(m)

        folium.Marker(
            location=[row["lat"], row["lon"]],
            icon=folium.DivIcon(
                html=f'<div style="font-size:12px;font-weight:bold;color:black;'
                     f'white-space:nowrap;transform:translate(12px,-6px);">'
                     f'{row["city"]}</div>'
            ),
        ).add_to(m)

    if bounds:
        m.fit_bounds(bounds, padding=(40, 40))

    output = MAPS_DIR / "map_top_5_destinations.html"
    m.save(str(output))
    print(f"[MAP] Top 5 destinations -> {output}")


def build_top20_hotels_map(df_top20: pd.DataFrame) -> None:
    """Carte avec 20 marqueurs numérotés + légende + panneau liste latéral."""
    # Déterminer les villes présentes et leurs couleurs
    cities_present = df_top20["city"].unique().tolist()
    color_map = {city: CITY_COLORS.get(city, DEFAULT_COLOR) for city in cities_present}

    m = folium.Map(
        location=[df_top20["plot_lat"].mean(), df_top20["plot_lon"].mean()],
        zoom_start=6,
        tiles="OpenStreetMap",
    )
    add_map_title(m, "Top 20 hôtels")

    bounds = []
    for _, row in df_top20.iterrows():
        city = clean_text(row["city"])
        hotel = clean_text(row["hotel_name"])
        score = row["hotel_score"]
        url = clean_text(row["url"])
        rank = int(row["rank"])
        color = color_map.get(city, DEFAULT_COLOR)

        bounds.append([row["plot_lat"], row["plot_lon"]])

        popup_html = (
            f"<b>Rang :</b> {rank}<br>"
            f"<b>Ville :</b> {city}<br>"
            f"<b>Hôtel :</b> {hotel}<br>"
            f"<b>Score hôtel :</b> {score}<br>"
            f'<b>Lien :</b> <a href="{url}" target="_blank">Booking</a>'
        )

        folium.CircleMarker(
            location=[row["plot_lat"], row["plot_lon"]],
            radius=10,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.85,
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=f"{rank}. {hotel}",
        ).add_to(m)

        folium.Marker(
            location=[row["plot_lat"], row["plot_lon"]],
            icon=folium.DivIcon(
                html=f'<div style="font-size:11px;font-weight:bold;color:black;'
                     f'text-align:center;width:18px;height:18px;line-height:18px;'
                     f'background-color:white;border:1px solid black;border-radius:50%;">'
                     f'{rank}</div>'
            ),
        ).add_to(m)

    if bounds:
        m.fit_bounds(bounds, padding=(40, 40))

    # Légende dynamique
    legend_items = "".join(
        f'<span style="color:{color_map[city]};">●</span> {city}<br>'
        for city in cities_present
    )
    m.get_root().html.add_child(folium.Element(
        f'<div style="position:fixed;bottom:35px;left:35px;width:220px;'
        f'background-color:white;border:2px solid grey;z-index:9999;'
        f'font-size:14px;padding:10px;box-shadow:2px 2px 6px rgba(0,0,0,0.2);">'
        f'<b>Légende villes</b><br>{legend_items}</div>'
    ))

    # Panneau liste latéral
    list_items = "".join(
        f'<li style="margin-bottom:10px;line-height:1.35;">'
        f'<span style="font-weight:700;">{shorten(r["hotel_name"], 46)}</span><br>'
        f'<span style="color:#555;">{r["city"]} — {r["hotel_score"]}</span></li>'
        for _, r in df_top20.sort_values("rank").iterrows()
    )
    m.get_root().html.add_child(folium.Element(
        f'<div style="position:fixed;top:90px;right:18px;width:320px;'
        f'max-height:72vh;overflow-y:auto;background-color:rgba(255,255,255,0.96);'
        f'border:1px solid #999;z-index:9999;padding:12px 14px;font-size:13px;'
        f'box-shadow:0 2px 8px rgba(0,0,0,0.20);border-radius:6px;">'
        f'<h4 style="margin:0 0 10px 0;">Top 20 hôtels</h4>'
        f'<ol style="padding-left:22px;margin:0;">{list_items}</ol></div>'
    ))

    output = MAPS_DIR / "map_top_20_hotels.html"
    m.save(str(output))
    print(f"[MAP] Top 20 hotels -> {output}")


def main() -> None:
    top_path = DATA_DIR / "top_cities.csv"
    final_path = DATA_DIR / "final_kayak_results.csv"

    if not top_path.exists():
        print(f"[ERREUR] Fichier introuvable : {top_path}")
        return
    if not final_path.exists():
        print(f"[ERREUR] Fichier introuvable : {final_path}")
        return

    df_top = pd.read_csv(top_path)
    df_final = pd.read_csv(final_path)

    # Cast des colonnes numériques
    for col in ["lat", "lon", "weather_score", "avg_temp_7d", "avg_pop_7d", "total_rain_7d", "avg_wind_7d"]:
        df_top[col] = pd.to_numeric(df_top[col], errors="coerce")

    df_final["lat"] = pd.to_numeric(df_final["lat"], errors="coerce")
    df_final["lon"] = pd.to_numeric(df_final["lon"], errors="coerce")
    df_final["hotel_score"] = pd.to_numeric(df_final["hotel_score"], errors="coerce").fillna(0)

    # Carte 1 : top 5 destinations
    df_top5 = df_top.sort_values("weather_score", ascending=False).head(5).copy()
    build_top5_map(df_top5)

    # Carte 2 : top 20 hôtels (par note client)
    df_top20 = (
        df_final
        .sort_values("hotel_score", ascending=False)
        .head(20)
        .copy()
        .reset_index(drop=True)
    )
    df_top20["rank"] = range(1, len(df_top20) + 1)
    df_top20 = prepare_visual_coordinates(df_top20)
    build_top20_hotels_map(df_top20)

    print(f"\n[RÉSULTAT] 2 cartes générées dans {MAPS_DIR}")


if __name__ == "__main__":
    main()
