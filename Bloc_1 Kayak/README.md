# Projet Kayak

> Pipeline ETL complet pour recommander les meilleures destinations kayak en France,
> en croisant données météo et offres hôtelières Booking.com.

**JEDHA Bootcamp — Bloc 1 — Data Collection & Management**

---

## Résultats obtenus

| Indicateur | Résultat |
|---|---|
| Villes géocodées | 35 / 35 |
| Villes avec données météo | 35 / 35 |
| Top destinations sélectionnées | 5 |
| Hôtels scrapés | 50 (10 par ville) |
| Lignes en base PostgreSQL | 50 |
| Cartes interactives générées | 2 |

### Top 5 destinations (résultats actuels)

| Rang | Ville | Score météo | Temp. moy. | Pluie totale | Vent moy. |
|---|---|---|---|---|---|
| 1 | Bayonne | 89.37 | 19.7 °C | 3.2 mm | 3.1 m/s |
| 2 | Aix en Provence | 89.30 | 20.0 °C | 2.8 mm | 2.9 m/s |
| 3 | Montauban | 88.60 | 19.1 °C | 3.0 mm | 3.3 m/s |
| 4 | Nîmes | 88.56 | 19.6 °C | 3.1 mm | 3.2 m/s |
| 5 | Avignon | 88.30 | 19.5 °C | 3.0 mm | 3.1 m/s |

---

## Architecture du pipeline

```
Nominatim          OpenWeather          Booking.com
(géocodage)    →   (prévisions)    →    (scraping)
     ↓                  ↓                   ↓
cities_geocoded    weather.csv       raw_booking_html/
     .csv               ↓                   ↓
                   top_cities.csv     hotels_multi_cities
                                           .csv
                              ↓
                   final_kayak_results.csv
                              ↓
                    Amazon S3  +  Neon PostgreSQL
                              ↓
                     Cartes Folium HTML
```

---

## Structure du projet

```
Bloc_1 Kayak/
├── data/
│   ├── raw_booking_html/          # Pages HTML brutes Booking (non versionnées)
│   ├── cities_geocoded.csv        # 35 villes + coordonnées GPS
│   ├── weather.csv                # Indicateurs météo + score pour 35 villes
│   ├── top_cities.csv             # Top 5 par score météo
│   ├── hotels_multi_cities.csv    # 50 hôtels (10 par ville)
│   └── final_kayak_results.csv    # Dataset final fusionné (50 × 12)
├── maps/
│   ├── map_top_5_destinations.html
│   └── map_top_20_hotels.html
├── src/
│   ├── geocode_cities.py          # Étape 1 — géocodage Nominatim
│   ├── weather.py                 # Étape 2 — météo OpenWeather
│   ├── select_top_cities.py       # Étape 3 — sélection top 5
│   ├── scrape_booking_raw.py      # Étape 4 — scraping Booking via ScrapingBee
│   ├── parse_booking.py           # Étape 5 — parsing HTML hôtels
│   ├── merge_results.py           # Étape 6 — fusion météo + hôtels
│   ├── load_to_neon.py            # Étape 7 — chargement PostgreSQL
│   ├── generate_maps.py           # Étape 8 — génération cartes Folium
│   └── run_pipeline.py            # Exécution du pipeline complet
├── Presentation/
│   └── Bloc 1_Kayak_Présentation.pptx
├── Kayak_Notebook.ipynb           # Notebook exécutable (pipeline complet commenté)
├── .env.example                   # Template à copier (créer .env localement)
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Installation

### Prérequis

- Python 3.10+
- Comptes actifs : [OpenWeather](https://openweathermap.org/), [ScrapingBee](https://www.scrapingbee.com/), [Neon](https://neon.tech/)

### 1. Cloner et installer les dépendances

```bash
git clone <url-du-repo>
cd "Bloc_1 Kayak"
pip install pandas requests beautifulsoup4 lxml folium psycopg2-binary python-dotenv
```

### 2. Configurer les clés API

```bash
cp .env.example .env
```

Remplir `.env` avec vos clés :

```env
OPENWEATHER_API_KEY=votre_cle_openweather
SCRAPINGBEE_API_KEY=votre_cle_scrapingbee
NEON_DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
```

---

## Utilisation

### Option A — Notebook (recommandé)

Ouvrir `Kayak_Notebook.ipynb` depuis la racine du projet et exécuter les cellules dans l'ordre. Chaque cellule est commentée.

```
Cellule 0  — Imports & chargement des clés
Cellule 1  — Géocodage Nominatim (35 villes)
Cellule 2  — Météo OpenWeather (35 villes)
Cellule 3  — Sélection Top 5
Cellule 4a — Test clé ScrapingBee
Cellule 4b — Scraping Booking (5 villes)
Cellule 5  — Parsing HTML hôtels
Cellule 6  — Fusion météo + hôtels
Cellule 7  — Chargement Neon PostgreSQL
Cellule 8  — Génération cartes Folium
Cellule 9  — Affichage des cartes
```

### Option B — Scripts Python

```bash
python src/geocode_cities.py
python src/weather.py
python src/select_top_cities.py
python src/scrape_booking_raw.py
python src/parse_booking.py
python src/merge_results.py
python src/load_to_neon.py
python src/generate_maps.py
```

---

## Détail des étapes

### 1. Géocodage — Nominatim (OpenStreetMap)

- **API** : Nominatim — gratuite, sans clé requise
- **Entrée** : liste de 35 villes françaises
- **Sortie** : `data/cities_geocoded.csv` (id, city, lat, lon)
- **Contrainte** : 1 requête/seconde max → `time.sleep(1.1)` entre chaque appel

### 2. Météo — OpenWeather `/forecast`

- **API** : OpenWeather plan gratuit — endpoint `/data/2.5/forecast`
- **Données** : prévisions toutes les 3h sur 5 jours (40 créneaux), agrégées par jour
- **Indicateurs** : température moyenne, probabilité de pluie, cumul pluie, vitesse vent
- **Sortie** : `data/weather.csv`

> **Note** : L'endpoint `/onecall` (7 jours) est réservé au plan payant.
> Le projet utilise `/forecast` (plan gratuit) avec agrégation sur 5 jours.

### 3. Score météo

Formule de scoring à partir de 100 points (température idéale = 24 °C) :

```
Score = 100
      − |temp_moy − 24| × 2.0    (écart à la température idéale)
      − prob_pluie × 30.0         (probabilité de pluie, de 0 à 1)
      − pluie_totale × 1.5        (cumul de précipitations en mm)
      − vent_moy × 0.8            (vitesse du vent en m/s)
```

### 4. Sélection Top 5

- Tri décroissant par `weather_score`
- Les 5 premières villes alimentent le scraping Booking
- **Sortie** : `data/top_cities.csv`

### 5. Scraping Booking — ScrapingBee

- **Pourquoi ScrapingBee ?** Booking bloque les requêtes Python directes. ScrapingBee simule un vrai navigateur avec proxy furtif et rendu JavaScript.
- **Stratégie** : 4 variantes d'URL testées par ville, on conserve la première qui retourne des fiches hôtels (`data-testid="property-card"`)
- **Sortie** : fichiers HTML dans `data/raw_booking_html/`

### 6. Parsing HTML — BeautifulSoup

- Extraction par `data-testid="property-card"` (sélecteur stable)
- Champs extraits : nom, note client (0-10), URL, description
- 10 hôtels maximum par ville → 50 au total
- **Sortie** : `data/hotels_multi_cities.csv`

### 7. Fusion météo + hôtels

- Jointure (`merge`) sur la colonne `city`
- Chaque hôtel hérite des indicateurs météo de sa ville
- **Sortie** : `data/final_kayak_results.csv` (50 lignes × 12 colonnes)

### 8. Stockage cloud

**Amazon S3** — organisation en 3 couches :
```
s3://bucket/
├── raw/          # HTML Booking bruts
├── processed/    # CSV intermédiaires
└── final/        # Dataset final + cartes
```

**Neon PostgreSQL** — table `kayak_results` :
```sql
SELECT COUNT(*) FROM kayak_results;  -- 50
```

### 9. Cartes interactives — Folium

| Carte | Contenu |
|---|---|
| `map_top_5_destinations.html` | 5 marqueurs avec indicateurs météo au clic |
| `map_top_20_hotels.html` | 20 hôtels numérotés, colorés par ville, panneau liste latéral |

> Les hôtels d'une même ville sont disposés en cercle autour du centre-ville
> (décalage trigonométrique) pour éviter la superposition des marqueurs.

---

## Dataset final

**`data/final_kayak_results.csv`** — 50 lignes × 12 colonnes :

| Colonne | Type | Description |
|---|---|---|
| `city` | string | Nom de la ville |
| `hotel_name` | string | Nom de l'hôtel |
| `hotel_score` | float | Note client Booking (0-10) |
| `url` | string | Lien vers la fiche Booking |
| `description` | string | Description de la chambre |
| `lat` | float | Latitude de la ville |
| `lon` | float | Longitude de la ville |
| `avg_temp_7d` | float | Température moyenne 5j (°C) |
| `avg_pop_7d` | float | Probabilité de pluie moyenne (0-1) |
| `total_rain_7d` | float | Cumul de pluie 5j (mm) |
| `avg_wind_7d` | float | Vitesse vent moyenne (m/s) |
| `weather_score` | float | Score météo calculé (/100) |

---

## Stack technique

| Outil | Rôle |
|---|---|
| **Nominatim** (OpenStreetMap) | Géocodage gratuit |
| **OpenWeather API** | Prévisions météo 5 jours |
| **ScrapingBee** | Scraping JS avec proxy anti-détection |
| **BeautifulSoup / lxml** | Parsing HTML |
| **pandas** | Manipulation et fusion des données |
| **Folium** | Cartes interactives HTML (Leaflet.js) |
| **psycopg2** | Connexion PostgreSQL |
| **Neon** | Base PostgreSQL cloud serverless |
| **Amazon S3** | Stockage fichiers cloud |
| **python-dotenv** | Gestion des clés API |

---

## Sécurité

- Le fichier `.env` contenant les clés API n'est **pas versionné** (`.gitignore`)
- Les fichiers HTML bruts `data/raw_booking_html/` sont **exclus du dépôt public**
- Copier `.env.example` → `.env` et remplir ses propres clés avant d'exécuter

---

## Limites identifiées

- Le score météo repose sur 5 jours de prévision (pas de données historiques)
- Les coordonnées GPS des hôtels sur la carte sont approximées au centre-ville
- Le scraping Booking peut être instable selon les mises à jour du site
- Le plan gratuit OpenWeather ne donne pas accès aux prévisions au-delà de 5 jours
