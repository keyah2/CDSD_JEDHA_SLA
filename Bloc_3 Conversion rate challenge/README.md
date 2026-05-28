# Challenge Conversion Rate — Prédiction de l'abonnement à la newsletter

## Vue d'ensemble
Ce projet traite un challenge de **classification binaire** : prédire si un visiteur va s'abonner à la newsletter **Data Science Weekly**.

Ce dépôt présente une version propre, lisible et reproductible du projet, construite pour rester ** alignée avec le brief officiel et la méthodologie du cours**.

## Contexte métier
L'entreprise souhaite mieux comprendre le comportement des visiteurs sur son site et identifier les principaux facteurs qui favorisent l'inscription à la newsletter.

La question centrale est la suivante :

> Peut-on prédire la conversion à partir d'un petit ensemble de variables utilisateur et session, puis transformer ce modèle en recommandations métier utiles ?

## Objectif du projet
- construire un modèle de prédiction de conversion ;
- l'évaluer avec la **métrique officielle : le F1-score** ;
- générer un fichier de soumission pour le jeu de test du challenge ;
- interpréter le modèle et proposer des recommandations métier.

## Données utilisées
Variables principales :
- `country`
- `age`
- `new_user`
- `source`
- `total_pages_visited`
- `converted` (cible, présente uniquement dans le train)

Fichiers utilisés :
- `data/conversion_data_train.csv`
- `data/conversion_data_test.csv`

## Méthodologie
Le projet suit une logique simple, propre et défendable :

1. **Audit rapide des données**  
   Vérification de la structure, des types, des valeurs manquantes et du déséquilibre de la cible.

2. **EDA orientée métier**  
   Analyse des distributions, des écarts entre convertis et non convertis, et mise en évidence des variables les plus informatives.

3. **Prétraitement avec scikit-learn**  
   - `OneHotEncoder` pour les variables catégorielles  
   - `StandardScaler` pour les variables numériques  
   - `ColumnTransformer` + `Pipeline` pour garantir un pipeline propre et réutilisable

4. **Modèle de base : régression logistique**  
   Choisie comme baseline car elle est solide, rapide, interprétable et très cohérente avec le niveau et les attentes du projet.

5. **Amélioration du modèle**  
   Ajustement du seuil de décision pour maximiser le **F1-score**, ce qui est particulièrement pertinent dans un contexte de classe positive rare.

6. **Comparaison non linéaire**  
   Test d'un modèle de type ensemble (`AdaBoost`) pour vérifier si une approche plus flexible améliore réellement le score.

7. **Interprétation métier et conclusion**  
   Lecture des coefficients du modèle retenu, traduction des résultats en recommandations concrètes, et rappel des limites.

## Résultats principaux
Version finale retenue :
- **Modèle** : `LogisticRegression(C=0.1)`
- **Seuil de décision** : `0.44`

Résultats observés sur validation :
- **F1-score** : `0.7771`
- **Precision** : `0.8446`
- **Recall** : `0.7195`

### Enseignements métier clés
- **`total_pages_visited`** est de loin le signal le plus fort.
- Les **visiteurs déjà revenus** convertissent bien mieux que les nouveaux.
- L'**âge** a un effet négatif sur la conversion.
- Le **pays** joue un rôle important, avec de meilleures performances pour `Germany` et `UK`, et une conversion plus faible pour `China`.

## Structure du projet
```text
conversion-rate-challenge/
├── README.md
├── .gitignore
├── data/
│   ├── conversion_data_train.csv
│   └── conversion_data_test.csv
├── notebooks/
│   ├── conversion_rate_challenge_executed.ipynb
│   └── conversion_rate_challenge_clean.ipynb
├── artifacts/
│   ├── conversion_rate_test_predictions.csv
│   ├── logistic_coefficients.csv
│   └── project_summary.json
└── pres/
    └── Bloc 3_Conversion_rate_challenge_présentation_.pptx
```

## Notebooks fournis
### 1. Notebook exécuté
`notebooks/conversion_rate_challenge_executed.ipynb`

À utiliser pour :
- montrer que le projet fonctionne ;
- afficher directement les tableaux, graphiques et résultats ;
- faciliter la lecture sur GitHub.


## Choix techniques
Pourquoi la régression logistique a été retenue :
- très bon niveau de performance après ajustement du seuil ;
- modèle stable ;
- interprétation directe des coefficients ;
- cohérence forte avec le brief ;
- meilleure lisibilité et interprétabilité qu'un modèle plus complexe et moins transparent.

## Limites du projet
- Le dataset contient peu de variables : certains facteurs de conversion réels ne sont probablement pas observés.
- Les coefficients du modèle ne prouvent pas une causalité stricte.
- Le seuil optimal a été ajusté sur validation : il faut toujours rappeler qu'il peut légèrement varier selon un autre découpage.
- Le comparaison non linéaire a été volontairement limité pour rester aligné avec le niveau pédagogique du projet.

## Pistes d'amélioration
- tester d'autres modèles d'ensemble plus avancés si le cadre du cours le permet ;
- approfondir l'analyse d'erreurs (faux positifs / faux négatifs) ;
- enrichir l'analyse métier par segment utilisateur ;
- ajouter une petite partie calibration / courbes de précision-rappel si souhaité pour aller plus loin.

## Technologies utilisées
- Python
- pandas
- numpy
- matplotlib
- seaborn
- scikit-learn

## Exécution du projet
### 1. Cloner le dépôt
```bash
git clone <URL_DU_REPO>
cd conversion-rate-challenge
```

### 2. Installer les dépendances
```bash
pip install pandas numpy matplotlib seaborn scikit-learn jupyter
```

### 3. Lancer Jupyter
```bash
jupyter notebook
```

### 4. Ouvrir le notebook
Ouvre ensuite :
- soit `notebooks/conversion_rate_challenge_executed.ipynb`
- soit `notebooks/conversion_rate_challenge_clean.ipynb`

## Conclusion
Ce projet montre qu'une approche simple, propre et bien justifiée peut être plus convaincante qu'un modèle plus complexe mal expliqué.


