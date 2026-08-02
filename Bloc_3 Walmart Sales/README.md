# Prévision des ventes hebdomadaires — Walmart

**Bloc 3 — Machine Learning supervisé | CDSD (Jedha / RNCP 35288)**

---

## Présentation

Ce projet construit un modèle de **régression supervisée** pour estimer les ventes hebdomadaires (`Weekly_Sales`) de magasins Walmart à partir de variables temporelles, commerciales et macroéconomiques.

La démarche couvre l'intégralité du cycle ML : exploration des données, préparation, modélisation, régularisation et interprétation des résultats.

---

## Objectif métier

Dans un contexte retail, estimer les ventes hebdomadaires permet de :
- anticiper l'activité des magasins et planifier les ressources
- mesurer l'impact du calendrier (périodes de fête, saisonnalité)
- mettre en perspective les variables économiques (chômage, CPI, carburant)
- appuyer des décisions marketing ou opérationnelles

> Ce projet reste un exercice pédagogique. Les résultats sont à lire comme une démonstration méthodologique.

---

## Données

| Fichier | Description |
|---|---|
| `data/Walmart_Store_sales.csv` | Dataset brut — 150 lignes, 8 colonnes |

**Variables disponibles :**

| Variable | Type | Rôle |
|---|---|---|
| `Store` | Catégorielle | Identifiant du magasin (1 à 20) |
| `Date` | Temporelle | Date de la semaine (JJ-MM-AAAA) |
| `Weekly_Sales` | Numérique | **Variable cible** — ventes en USD |
| `Holiday_Flag` | Catégorielle | Semaine de fête (1) ou ordinaire (0) |
| `Temperature` | Numérique | Température locale (°F) |
| `Fuel_Price` | Numérique | Prix du carburant (USD/gallon) |
| `CPI` | Numérique | Indice des prix à la consommation |
| `Unemployment` | Numérique | Taux de chômage local (%) |

---

## Démarche

### 1. Analyse exploratoire (EDA)
- Distribution de `Weekly_Sales` et détection des valeurs aberrantes
- Analyse des ventes par magasin — forte hétérogénéité inter-magasins
- Saisonnalité mensuelle et annuelle
- Impact des semaines de fête (effectif faible : <10% du dataset)
- Matrice de corrélation et scatter plots des variables économiques

### 2. Preprocessing
- **Suppression** des lignes sans `Weekly_Sales` (jamais d'imputation sur la cible)
- **Feature engineering** : extraction de `Year`, `Month`, `Day`, `DayOfWeek` depuis `Date`
- **Imputation de `Holiday_Flag`** par calendrier américain (Super Bowl, Labour Day, Thanksgiving, Christmas) — plus fiable qu'une imputation statistique
- **Suppression des outliers** par règle des 3 sigma sur les variables économiques continues

### 3. Pipeline sklearn
- **Variables numériques** : `KNNImputer(k=5)` + `StandardScaler`
  - Le KNN exploite les corrélations entre variables (plus précis que la médiane)
  - La standardisation est obligatoire pour Ridge et Lasso
- **Variables catégorielles** : `SimpleImputer(most_frequent)` + `OneHotEncoder(drop='first')`
  - `drop='first'` évite la multicolinéarité parfaite

### 4. Modèles comparés

| Modèle | Particularité |
|---|---|
| `LinearRegression` | Baseline sans pénalité |
| `Ridge` (L2) | Réduit tous les coefficients, aucun à zéro |
| `Lasso` (L1) | Peut forcer des coefficients exactement à zéro (sélection de features) |

Les hyperparamètres `alpha` de Ridge et Lasso sont optimisés par `GridSearchCV` (CV 5 folds, plage logarithmique).

---

## Résultats

| Modèle | R² Test | RMSE Test | MAE Test | CV RMSE | ΔR² |
|---|---:|---:|---:|---:|---:|
| LinearRegression (baseline) | 0.9019 | 184 565 USD | 145 692 USD | 150 262 USD | 0.0745 |
| Ridge (α=1.0, défaut) | 0.8719 | 210 955 USD | 181 608 USD | 240 948 USD | 0.0691 |
| Lasso (α=1.0, défaut) | 0.9019 | 184 554 USD | 145 692 USD | 150 252 USD | 0.0745 |
| Ridge optimisé (α=0.001) | 0.9020 | 184 486 USD | 145 624 USD | 153 377 USD | 0.0744 |
| **Lasso optimisé (α=646)** | **0.9068** | **179 925 USD** | **146 433 USD** | **149 449 USD** | **0.0690** |

**Modèle retenu : Lasso optimisé (α=646)** — meilleur RMSE test, meilleur R² test, meilleure stabilité en validation croisée et surapprentissage le plus faible.

Points notables :
- Le Ridge optimisé trouve α=0.001 (quasi-nul) → la régularisation L2 n'apporte rien sur ce dataset
- Le Lasso annule seulement 2 features sur 27 → modèle quasi-complet
- Le Ridge avec α=1.0 par défaut est **sur-régularisé** et donne les pires résultats (RMSE +14%)

---

## Enseignements principaux

1. **Le magasin est le prédicteur dominant** : les 14 features les plus importantes sont toutes des dummies `Store`, avec des coefficients jusqu'à ±1 345 000 USD. L'hétérogénéité de taille entre magasins explique l'essentiel des ventes.
2. **Saisonnalité confirmée** : `Month` apparaît parmi les features significatives — pics de ventes en décembre et en été.
3. **Variables économiques à faible corrélation** : CPI (r=−0.29), Temperature (r=−0.17), Unemployment (r=+0.06), Fuel_Price (r=−0.02). Leur impact individuel est marginalisé par la variance inter-magasins.
4. **`DayOfWeek` sans pouvoir prédictif** : 132 dates sur 132 sont des vendredis — variable quasi-constante, annulée par le Lasso.
5. **Biais résiduel de −87 374 USD** : le modèle sous-estime systématiquement les ventes des plus grands magasins.

---

## Limites et pistes d'amélioration

| Limite | Piste |
|---|---|
| Dataset très petit (~131 lignes après nettoyage) | Dataset complet Kaggle (~6 000 lignes) |
| Semaines de fête sous-représentées (<10%) | Sur-échantillonnage ou pondération |
| Modèle strictement linéaire | Random Forest, XGBoost |
| Pas de données sur la taille des magasins | Ajouter surface, type (A/B/C) |
| Pas de données promotionnelles | Enrichissement du dataset |

---

## Structure du dépôt

```text
Bloc_3 Walmart Sales/
├── .gitignore
├── README.md
├── requirements.txt
├── data/
│   └── Walmart_Store_sales.csv
├── Notebooks/
│   ├── walmart_weekly_sales_clean.ipynb    ← version sans outputs, relançable
│   └── walmart_weekly_sales_executed.ipynb ← version avec résultats
└── pres/
    └── Bloc3_Walmart_Presentation.pptx
```

---

## Utilisation

### Consulter le projet
Ouvrir `Notebooks/walmart_weekly_sales_executed.ipynb` pour le notebook principal commenté en français.

### Réexécuter le projet
```bash
pip install -r requirements.txt
```
Puis ouvrir `Notebooks/walmart_weekly_sales_executed.ipynb` et exécuter les cellules dans l'ordre.

> Le notebook détecte automatiquement le chemin des données (`../data/` ou `data/`) selon le répertoire de lancement.

---

## Technologies

- Python 3.10+
- pandas, NumPy, SciPy
- Matplotlib, Seaborn
- scikit-learn
- Jupyter Notebook

