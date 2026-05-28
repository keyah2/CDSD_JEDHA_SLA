# Analyse exploratoire du marché Steam — Databricks & PySpark

## Contexte

Dans le cadre du bloc Big Data de la certification JEDHA, Ubisoft souhaite disposer d'une lecture globale de l'écosystème Steam afin de mieux comprendre les tendances du marché vidéoludique.

Ce projet répond à cette demande en exploitant un dataset Steam semi-structuré avec **PySpark sur Databricks**, conformément aux exigences de l'énoncé.

## Données

- **Source** : `s3://full-stack-bigdata-datasets/Big_Data/Project_Steam/steam_game_output.json`
- **Format** : JSON semi-structuré avec schéma imbriqué
- **Volume** : 55 691 jeux

## Stack technique

| Catégorie | Outil |
|---|---|
| Langage | Python |
| Traitement distribué | PySpark |
| Environnement | Databricks |
| Visualisation | Databricks display() + Matplotlib |
| Stockage source | AWS S3 |

## Structure du dépôt

```
.
├── notebooks/
│   └── steam_analysis.ipynb   ← Notebook exécuté avec outputs
└── README.md
```

## Contenu du notebook

Le notebook `steam_analysis.ipynb` couvre les analyses suivantes :

### Analyse macro
- Quel éditeur a publié le plus de jeux sur Steam ?
- Quels sont les jeux les mieux notés ?
- Y a-t-il des années avec plus de sorties ? Impact du Covid ?
- Comment les prix sont-ils distribués ? Y a-t-il beaucoup de promotions ?
- Quelles sont les langues les plus représentées ?
- Y a-t-il beaucoup de jeux interdits aux moins de 16/18 ans ?

### Analyse par genre et plateforme
- Quels sont les genres les plus représentés ?
- Certains genres ont-ils un meilleur ratio d'avis positifs ?
- Certains éditeurs ont-ils des genres de prédilection ?
- Quels sont les genres les plus lucratifs ?
- Répartition des jeux sur Windows, Mac et Linux
- Certains genres sont-ils préférentiellement disponibles sur certaines plateformes ?

## Principaux résultats

- **Big Fish Games** est l'éditeur le plus prolifique (422 jeux), devant SEGA et Square Enix
- Le genre **Indie** domine avec 39 681 jeux, suivi d'Action et Casual
- **Windows** représente la plateforme quasi-exclusive (99,9 % des jeux)
- Seulement **4,52 %** des jeux sont en promotion
- **0,47 %** du catalogue est restreint aux 16 ans et plus
- Le genre **Action** génère les revenus estimés les plus élevés

## Exécution

Le notebook est conçu pour être exécuté dans Databricks. Le cluster doit avoir accès au bucket S3 JEDHA.

1. Importer `steam_analysis.ipynb` dans Databricks
2. Démarrer le cluster
3. Exécuter toutes les cellules dans l'ordre
