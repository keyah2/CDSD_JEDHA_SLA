# Détecteur de fraude e-commerce

Ce projet présente une application de détection de fraude sur des transactions e-commerce. Il combine une analyse exploratoire, un modèle de classification supervisée et une interface Streamlit permettant d’auditer des transactions unitaires ou des fichiers CSV.

L’objectif est de proposer une démarche complète, lisible et reproductible : comprendre les données, entraîner un modèle adapté à une cible déséquilibrée, interpréter les résultats, puis rendre le modèle exploitable dans une application simple.

---

## Contexte business

La fraude e-commerce représente un risque financier direct pour les plateformes de paiement, les commerçants et les utilisateurs. Lorsqu’un volume important de transactions est traité, l’analyse manuelle devient difficile à maintenir sans outil de priorisation.

Ce projet vise à identifier automatiquement les transactions présentant un risque élevé de fraude. L’enjeu n’est pas seulement de prédire une classe, mais de produire une information exploitable pour aider une équipe métier à prioriser ses contrôles.

Dans ce contexte, deux contraintes doivent être équilibrées :

- limiter les fraudes non détectées ;
- éviter un volume excessif de fausses alertes.

---

## Objectifs du projet

L’objectif principal est de construire un système de détection de fraude capable d’estimer le risque associé à une transaction e-commerce.

Les objectifs secondaires sont :

- analyser les variables transactionnelles et comportementales ;
- préparer les données pour un modèle supervisé ;
- entraîner un modèle adapté à une cible fortement déséquilibrée ;
- interpréter les prédictions et les variables influentes ;
- proposer une application Streamlit permettant de tester le modèle.

Les livrables principaux sont :

- un notebook d’analyse et de modélisation ;
- une application Streamlit ;
- des exemples de transactions au format JSON ;
- un échantillon CSV pour tester l’application ;
- des captures d’écran illustrant le fonctionnement de l’interface.

---

## Données utilisées

Le projet s’appuie sur un jeu de données de transactions e-commerce utilisé pour un cas de détection de fraude.

Les données contiennent notamment des informations relatives :

- au montant des transactions ;
- à l’ancienneté du compte utilisateur ;
- au comportement transactionnel ;
- aux signaux de sécurité de paiement ;
- à la cohérence géographique entre client, carte et livraison ;
- à la variable cible `is_fraud`.

Le fichier brut complet `transactions.csv` n’est pas inclus dans ce dépôt afin de conserver un repository léger. Des fichiers d’exemple sont fournis dans le dossier `data/` pour tester l’application.

---

## Méthodologie

La démarche suit une progression classique de projet machine learning.

### 1. Compréhension des données

La première étape consiste à analyser la structure du dataset, les types de variables, les valeurs manquantes, la distribution des montants et la répartition de la cible.

### 2. Analyse exploratoire

L’analyse exploratoire permet d’identifier les signaux associés à la fraude : comportements inhabituels, incohérences géographiques, contrôles de sécurité ou encore activité récente de l’utilisateur.

### 3. Préparation et transformation

Les données sont préparées pour l’entraînement du modèle : traitement des variables numériques, encodage des variables catégorielles, création de variables métier et séparation entre données d’entraînement et données de test.

### 4. Modélisation

Plusieurs approches de classification sont étudiées. Le modèle final retenu est un modèle XGBoost, adapté aux données tabulaires et aux relations non linéaires entre variables.

### 5. Évaluation

L’évaluation tient compte du déséquilibre de classes. L’accuracy seule n’est pas suffisante : le rappel, la précision, le F1-score et la matrice de confusion sont plus pertinents pour analyser la qualité de détection des fraudes.

### 6. Interprétation et mise à disposition

Les résultats sont interprétés à l’aide des importances de variables et de SHAP. Le modèle est ensuite rendu accessible via une application Streamlit permettant de tester des transactions unitaires ou des fichiers CSV.

---

## Résultats clés

Le modèle XGBoost final obtient un compromis cohérent entre détection des fraudes et maîtrise des fausses alertes.

| Élément analysé | Résultat principal | Interprétation |
|---|---:|---|
| Volume du dataset | 299 695 transactions | Base suffisante pour entraîner et évaluer un modèle supervisé |
| Taux de fraude | Environ 2,2 % | Problème fortement déséquilibré |
| Recall fraude | Environ 0,83 | Le modèle détecte une majorité des fraudes du jeu de test |
| Precision fraude | Environ 0,79 | Les alertes positives restent majoritairement pertinentes |
| F1-score fraude | Environ 0,81 | Bon équilibre entre rappel et précision |
| Faux négatifs | 222 | Fraudes non détectées, point critique à surveiller |
| Faux positifs | 289 | Alertes injustifiées, mais volume maîtrisé |

Ces résultats doivent être interprétés dans une logique métier : selon le coût d’une fraude non détectée et le coût d’une vérification inutile, le seuil de décision peut être ajusté.

---

## Principaux enseignements

La fraude ne repose pas sur un signal unique. Elle est mieux détectée en combinant plusieurs familles de variables : comportement utilisateur, historique transactionnel, signaux de sécurité, distance de livraison et cohérence géographique.

Le choix de XGBoost est pertinent pour ce type de données, car il permet de modéliser des interactions complexes entre variables tout en conservant de bonnes performances sur des données structurées.

D’un point de vue opérationnel, l’application peut servir d’outil d’aide à la priorisation. Elle ne remplace pas une décision métier finale, mais elle permet d’identifier rapidement les transactions à examiner en priorité.

---

## Structure du dépôt

```text
.
├── app.py
├── assets/
│   ├── feature0.json
│   ├── feature1.json
│   ├── target0.json
│   ├── target1.json
│   ├── logo_g4.jpg
│   └── logo_G4_antifraude.jpg
├── data/
│   ├── X_test_app_sample.csv
│   └── y_test_app_sample.csv
├── models/
│   └── .gitkeep
├── notebooks/
│   ├── detecteur_fraude_xgboost_executed.ipynb
│   └── detecteur_fraude_xgboost_clean.ipynb
├── pres/
│   └── BLOC_6_Detection fraud_.pptx
├── Dockerfile
├── setup_mlflow.py
├── start_mlflow.py
├── requirements.txt
├── .dockerignore
├── .gitattributes
├── .gitignore
└── README.md
```

Le dossier `models/` est conservé avec un fichier `.gitkeep` afin de garder une structure claire sans versionner de modèle binaire lourd dans le dépôt.

---

## Technologies utilisées

| Catégorie | Outils |
|---|---|
| Langage | Python |
| Analyse de données | Pandas, NumPy |
| Visualisation | Matplotlib, Seaborn |
| Machine learning | Scikit-learn, XGBoost |
| Optimisation | Optuna |
| Interprétabilité | SHAP |
| Application | Streamlit |
| Déploiement | Docker |
| Environnement | Jupyter Notebook |

---

## Exécuter le projet

### 1. Cloner le dépôt

```bash
git clone <URL_DU_REPO>
cd detection-fraude
```

### 2. Créer un environnement virtuel

```bash
python -m venv .venv
```

Sous Windows :

```bash
.venv\Scripts\activate
```

Sous macOS ou Linux :

```bash
source .venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Lancer l’application Streamlit

```bash
streamlit run app.py
```

L’application charge les artefacts nécessaires au fonctionnement du modèle si ceux-ci ne sont pas présents localement.

---

## Notebooks disponibles

| Notebook | Description |
|---|---|
| `notebooks/detecteur_fraude_xgboost_executed.ipynb` | Version exécutée avec résultats, graphiques et sorties visibles |
| `notebooks/detecteur_fraude_xgboost_clean.ipynb` | Version sans outputs, plus légère et relançable |

Pour relancer complètement l’entraînement, le fichier brut `transactions.csv` doit être disponible localement. Il n’est pas inclus dans ce dépôt.

---

## Utilisation de l’application

L’application Streamlit propose deux usages principaux.

### Audit unitaire

L’utilisateur peut tester une transaction individuelle afin d’obtenir :

- une prédiction ;
- un score de risque ;
- une lecture des facteurs qui influencent la décision du modèle.

### Audit de masse

L’utilisateur peut charger un fichier CSV afin d’analyser plusieurs transactions et d’identifier celles qui présentent un risque élevé.

Des fichiers d’exemple sont fournis pour tester rapidement l’application.

---

## Limites

Plusieurs limites doivent être prises en compte :

- le dataset reste un jeu de données d’exercice ;
- la fraude est une classe minoritaire, ce qui rend l’évaluation sensible au choix des métriques ;
- le seuil de décision doit être ajusté selon le contexte métier ;
- les comportements frauduleux peuvent évoluer dans le temps ;
- le dépôt ne contient pas le fichier brut complet ni le modèle binaire lourd ;
- une mise en production réelle nécessiterait un suivi de dérive, une surveillance des performances et une gouvernance du modèle.

---

## Pistes d’amélioration

Des améliorations réalistes pourraient être apportées :

- tester plusieurs seuils de décision selon différents scénarios métier ;
- mettre en place un suivi de dérive des données ;
- versionner les modèles et les jeux de features ;
- ajouter des tests automatisés sur les fonctions critiques ;
- enrichir les variables comportementales ;
- intégrer un pipeline d’entraînement reproductible ;
- suivre les performances du modèle dans le temps.

---

## Conclusion

Ce projet met en place une chaîne complète de détection de fraude, depuis l’analyse des transactions jusqu’à une application Streamlit utilisable pour tester des cas concrets.

Le modèle XGBoost retenu fournit un compromis pertinent entre rappel et précision sur une cible fortement déséquilibrée. L’application rend le modèle plus concret en exposant les prédictions, les scores de risque et les principaux facteurs d’influence.

Le projet constitue une base solide pour comprendre les enjeux techniques et métier d’un système de détection de fraude appliqué à des transactions e-commerce.
