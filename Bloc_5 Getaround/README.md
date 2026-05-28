# GetAround — analyse des retards et API de prédiction de prix

## Présentation

Ce projet répond à deux besoins complémentaires autour du cas GetAround.

Le premier consiste à analyser les retards entre deux locations afin d'identifier une règle de délai minimal permettant de réduire les conflits opérationnels. Le second consiste à entraîner un modèle de prédiction du prix journalier d'un véhicule et à l'exposer via une API FastAPI.

Le dépôt regroupe donc une analyse métier, un tableau de bord Streamlit, une API de prédiction et les scripts nécessaires pour reproduire les principaux résultats.

## Sommaire

- [Contexte business](#contexte-business)
- [Objectifs du projet](#objectifs-du-projet)
- [Données utilisées](#données-utilisées)
- [Méthodologie](#méthodologie)
- [Résultats clés](#résultats-clés)
- [Principaux enseignements](#principaux-enseignements)
- [Structure du dépôt](#structure-du-dépôt)
- [Technologies utilisées](#technologies-utilisées)
- [Exécution du projet](#exécution-du-projet)
- [Notebooks disponibles](#notebooks-disponibles)
- [Limites du projet](#limites-du-projet)
- [Pistes d'amélioration](#pistes-damélioration)
- [Conclusion](#conclusion)

## Contexte business

GetAround doit limiter les incidents liés aux retours tardifs.

Lorsqu'un véhicule est rendu trop tard, la location suivante peut être retardée, dégradée, voire impossible à honorer. L'enjeu consiste donc à trouver un compromis défendable entre :

- la **protection opérationnelle** ;
- l'**impact commercial** d'un délai minimal imposé entre deux réservations.

En parallèle, la plateforme a besoin d'un service simple permettant d'estimer un **prix journalier de location** à partir des caractéristiques d'un véhicule. C'est le rôle de l'API FastAPI fournie dans ce dépôt.

## Objectifs du projet

### Objectif principal

Déterminer une règle de délai minimal pertinente pour réduire les conflits entre locations successives.

### Objectifs secondaires

- construire un tableau de bord Streamlit lisible et orienté décision ;
- comparer plusieurs approches pour la prédiction du prix journalier ;
- exposer le modèle retenu via une API FastAPI ;
- proposer une structure de dépôt claire, exécutable localement, publiable sur GitHub et déployable.

### Livrables produits

- une application Streamlit : `app.py` ;
- une API FastAPI : `api/app.py` ;
- deux notebooks : une version exécutée et une version clean ;
- des scripts d'analyse et d'entraînement ;

## Données utilisées

| Jeu de données | Description | Format |
|---|---|---|
| `get_around_delay_analysis.xlsx` | Historique des locations utilisé pour l'analyse des retards | Excel |
| `get_around_pricing_project.csv` | Données véhicules utilisées pour la prédiction du prix journalier | CSV |
| `threshold_simulation.csv` | Résultats agrégés des simulations de seuils | CSV |
| `business_summary.json` | Synthèse métier de l'analyse des retards | JSON |
| `pricing_metrics.json` | Résultats de comparaison des modèles de prix | JSON |

Repères utiles sur les données de retards :

- **21 310** locations au total ;
- **1 841** locations liées à une location précédente ;
- **218** cas réellement problématiques dans l'enchaînement de deux locations.

## Méthodologie

### 1. Analyse des retards

- chargement et contrôle de la structure des données ;
- identification des locations dépendantes d'une location précédente ;
- simulation de plusieurs seuils de délai minimal ;
- comparaison entre protection opérationnelle et impact global.

### 2. Prédiction du prix journalier

- préparation du dataset véhicules ;
- comparaison de plusieurs modèles ;
- sélection du modèle retenu sur la base des métriques de holdout ;
- exposition du modèle via FastAPI.

### 3. Mise en forme du projet

- tableau de bord Streamlit pour la lecture métier ;
- API documentée automatiquement via `/docs` ;
- scripts reproductibles ;

## Résultats clés

| Élément analysé | Résultat principal | Interprétation |
|---|---|---|
| Politique recommandée | **120 minutes sur l'ensemble du parc** | Premier seuil franchissant un niveau élevé de protection tout en gardant un impact limité |
| Cas problématiques résolus | **180** cas, soit **82,6 %** | Réduction forte des incidents opérationnels |
| Locations affectées | **666** locations, soit **3,1 %** du total | Impact commercial mesuré et contenu |
| Option conservatrice | **120 minutes sur Connect uniquement** | Option moins intrusive mais nettement moins protectrice |
| Modèle de prix retenu | **RandomForest** | Meilleur compromis parmi les modèles comparés |
| Performance du modèle | **MAE 10,75 €/jour**, **RMSE 16,95**, **R² 0,727** | Niveau cohérent pour un cas pédagogique de pricing |

## Principaux enseignements

- Le vrai sujet n'est pas le retard brut, mais le **retard qui perturbe la location suivante**.
- Un seuil de **120 minutes** appliqué à l'ensemble du parc constitue ici le meilleur compromis opérationnel.
- Une politique limitée à **Connect** réduit davantage l'impact commercial, mais laisse trop d'incidents non résolus.
- Le volet pricing complète utilement le projet en montrant une chaîne cohérente : **analyse métier → modèle → API**.

## Structure du dépôt

```text
.
├── app.py
├── Dockerfile.dashboard
├── Makefile
├── MLproject
├── README.md
├── requirements.txt
├── .gitignore
├── api/
│   ├── app.py
│   ├── Dockerfile
│   ├── sample_payload_dict.json
│   └── sample_payload_list.json
├── assets/
├── data/
├── models/
├── notebooks/
│   ├── getaround_analysis_executed.ipynb
│   └── getaround_analysis_clean.ipynb
├── PRES/
│   └── Bloc 5_Get Around_presentation.pptx
├── src/
└── tests/
```

## Technologies utilisées

| Catégorie | Outils |
|---|---|
| Langage | Python |
| Analyse de données | Pandas, NumPy, openpyxl |
| Visualisation | Plotly, Matplotlib |
| Machine Learning | scikit-learn, joblib |
| API | FastAPI, Uvicorn, Pydantic |
| Application | Streamlit |
| Suivi d'expériences | MLflow |
| Tests | pytest |
| Conteneurisation | Docker |

## Exécution du projet

### Installation

```bash
git clone <URL_DU_REPO>
cd getaround-project
pip install -r requirements.txt
```

### Lancer le tableau de bord

```bash
streamlit run app.py
```

### Lancer l'API

```bash
uvicorn api.app:app --reload
```

### Lancer les tests

```bash
pytest -q
```

### Commandes utiles via Makefile

```bash
make dashboard
make api
make test
make train
make analyze
```

## Notebooks disponibles

| Notebook | Description |
|---|---|
| `getaround_analysis_executed.ipynb` | Version exécutée avec résultats, tableaux et graphiques visibles |
| `getaround_analysis_clean.ipynb` | Même structure, sans outputs, pour une relance propre |

## Limites du projet

- Le fichier d'analyse des retards ne contient pas de variable de chiffre d'affaires ; l'impact commercial est donc approché via le nombre de locations affectées.
- La recommandation de seuil repose sur les données fournies et ne remplace pas un test en production.
- Le modèle de prix est adapté à un cas pédagogique et à une démonstration API, mais ne remplace pas un système industriel complet.
- Le fichier modèle `.joblib` n'est pas versionné sur GitHub en raison de sa taille. Pour relancer l'API localement après un clone, il faut régénérer le modèle avec `make train` ou `python src/train_model.py`.

## Pistes d'amélioration

- tester la recommandation sur des segments de véhicules ou de villes ;
- enrichir les données de prix avec davantage de variables contextuelles ;
- ajouter une validation plus fine du modèle et du drift ;
- brancher le modèle sur un registre MLflow distant ;
- industrialiser davantage le déploiement avec CI/CD.

## Conclusion

Ce projet traite dans un même dépôt une question produit et une question de machine learning.

L'analyse des retards conduit à une recommandation claire : **imposer 120 minutes de délai minimal sur l'ensemble du parc**. Le volet API montre ensuite comment transformer un modèle de prédiction en service exploitable.

L'ensemble reste volontairement sobre.
