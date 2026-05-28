# Analyse des déterminants d'un match mutuel — Dataset *Speed Dating*

Projet d'analyse exploratoire de données réalisé dans le cadre du **Bloc 2 Jedha**.  
L'objectif est d'identifier les variables les plus associées à une **décision positive** (`dec`) puis à un **match mutuel** (`match`) dans le dataset *Speed Dating*, en adoptant une lecture **orientée produit** pour un cas d'usage type application de rencontre.

---

## Problématique

> **Quels facteurs augmentent réellement la probabilité qu'un rendez-vous débouche sur un intérêt réciproque ?**

Le projet cherche notamment à distinguer :

- ce qui relève du **profil avant la rencontre** ;
- ce qui se construit **pendant l'interaction** ;
- et les signaux les plus utiles dans une logique de matching produit.

---

## Démarche d'analyse

1. Chargement des données et compréhension de la structure
2. Clarification de l'unité d'analyse (ligne, participant, paire)
3. Vérification de la qualité des données
4. Étude des deux cibles business : `dec` et `match`
5. Analyse des préférences déclarées et des variables observées pendant l'interaction
6. Étude des questions du brief :
   - attractiveness
   - intérêts partagés vs même race
   - calibration des participants
   - ordre de passage dans la soirée
   - variables de contexte (écart d'âge)
7. Bonus de modélisation : comparaison profil seul vs impressions du rendez-vous

---

## Jeu de données

Le projet s'appuie sur le dataset classique **Speed Dating** recueilli lors d'événements expérimentaux au début des années 2000.

| Indicateur | Valeur |
|---|---|
| Lignes | 8 378 |
| Speed dates uniques | 4 184 |
| Participants uniques | 551 |
| Vagues | 21 |

Chaque ligne représente **la perception d'un participant pour un rendez-vous donné**.  
Un même rendez-vous apparaît donc généralement **deux fois** dans la table brute.

---

## Principaux enseignements

- Le **match mutuel** reste relativement rare
- Les hommes disent plus souvent **oui**, mais cela ne produit pas davantage de matches mutuels
- Les signaux les plus fortement associés à une issue positive sont surtout :
  - l'**appréciation globale** (`like`)
  - le **fun**
  - les **intérêts partagés**
  - et l'**attractiveness**
- La simple proximité démographique est bien moins informative que la **compatibilité vécue pendant l'échange**
- Les participants ont une **intuition partielle** de leur succès, mais restent globalement **mal calibrés**
- Les variables de **profil seules** expliquent peu le résultat final

---

## Implications produit

- Les variables de profil doivent être considérées comme des **signaux faibles** ou des **priors**
- Les variables traduisant une **compatibilité concrète** sont beaucoup plus utiles
- Un bon système de matching ne doit pas seulement rapprocher des profils "semblables", mais favoriser les combinaisons susceptibles de générer une interaction fluide et agréable

---

## Structure du dépôt

```
Bloc_2 Tinder/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── speed_dating_data.csv
│   └── speed_dating_data_key.doc
└── notebooks/
    └── speed_dating_tinder_analysis.ipynb
```

---

## Installation et exécution

### 1. Cloner le dépôt

```bash
git clone <URL_DU_REPO>
cd "Bloc_2 Tinder"
```

### 2. Créer un environnement

```bash
conda create -n speed_dating python=3.11 -y
conda activate speed_dating
pip install -r requirements.txt
```

### 3. Lancer le notebook

```bash
jupyter notebook notebooks/speed_dating_tinder_analysis.ipynb
```

Exécuter les cellules dans l'ordre avec **Run All**.

---

## Limites

- Le dataset provient d'un **speed dating expérimental** datant du début des années 2000
- Plusieurs variables très informatives sont mesurées **après interaction**
- Les observations ne sont pas totalement indépendantes (un même participant apparaît plusieurs fois)
- Certaines colonnes comportent beaucoup de valeurs manquantes
