# Détection de SMS indésirables avec le deep learning — AT&T

## En bref

- **Problème** : classifier automatiquement des SMS en `ham` ou `spam`
- **Données** : 5 572 messages annotés (4 825 ham / 747 spam)
- **Approche** : préparation de texte, tokenization, padding, comparaison de 3 modèles de deep learning dont un modèle de transfer learning
- **Modèle retenu** : `Embedding + GlobalAveragePooling1D` — F1-score : **0.9448**

---

## Présentation du projet

Ce projet vise à construire un modèle de **classification binaire** capable de prédire si un SMS est un **spam** ou un **ham** (message normal) à partir du seul contenu textuel du message.

Le cas d’usage est simple et concret : automatiser la détection de SMS indésirables afin de réduire l’exposition des utilisateurs à des messages promotionnels, frauduleux ou non sollicités.

Le projet a été réalisé dans un cadre pédagogique, avec une approche volontairement sobre, reproductible et alignée avec les attendus d’un projet de deep learning appliqué au texte.

---

## Contexte métier

La détection automatique de spam est un problème fréquent dans les télécommunications et les services numériques.

Un tel modèle peut contribuer à :

- filtrer automatiquement les messages suspects ;
- réduire les faux messages promotionnels ou frauduleux ;
- améliorer l’expérience utilisateur ;
- assister un système de modération ou de pré-classification.

Dans ce contexte, l’objectif n’est pas seulement d’obtenir de bonnes performances, mais aussi de construire une solution **simple, cohérente et défendable**.

---

## Objectifs du projet

L’objectif principal est de répondre à la question suivante :

> Peut-on détecter efficacement un SMS spam à partir du seul texte du message ?

Pour y répondre, le projet suit les étapes suivantes :

1. chargement et exploration des données ;
2. préparation et encodage des messages ;
3. transformation du texte en séquences numériques ;
4. entraînement de plusieurs modèles de deep learning ;
5. comparaison des performances ;
6. sélection du modèle le plus pertinent.

---

## Données utilisées

Le projet repose sur le fichier `spam.csv`, qui contient **5 572 SMS** annotés selon deux classes :

- **ham** : message normal
- **spam** : message indésirable

Après nettoyage, seules deux colonnes sont conservées :

- `label` : la classe du message
- `text` : le contenu du SMS

### Répartition des classes

- **ham** : 4 825 messages
- **spam** : 747 messages

Le dataset est donc **déséquilibré**, ce qui justifie l’utilisation de plusieurs métriques d’évaluation au-delà de la seule accuracy.

---

## Méthodologie

### 1. Préparation des données

Les principales étapes de préparation sont les suivantes :

- suppression des colonnes inutiles ;
- renommage des colonnes utiles ;
- encodage des labels :
  - `ham -> 0`
  - `spam -> 1`
- séparation entre variables explicatives (`X`) et variable cible (`y`) ;
- division en jeu d’entraînement et jeu de test avec `train_test_split` ;
- tokenization du texte ;
- transformation des SMS en séquences numériques ;
- padding des séquences pour uniformiser leur longueur.

### 2. Modèles testés

Trois architectures de deep learning ont été comparées :

#### Modèle 1 — Embedding + GlobalAveragePooling1D
Baseline simple et léger. L’embedding est entraîné from scratch, le GlobalAveragePooling1D agrège les représentations de chaque mot.

#### Modèle 2 — Embedding + LSTM
Architecture récurrente qui modélise l’ordre des mots dans la séquence.

#### Modèle 3 — Transfer Learning (NNLM via TensorFlow Hub)
Utilisation d’un encodeur pré-entraîné sur des milliards de mots du corpus Google News. Fine-tuning sur nos données.

---

## Résultats clés

Les performances ont été évaluées à l’aide des métriques suivantes :

- **Accuracy**
- **Precision**
- **Recall**
- **F1-score**

### Comparaison des modèles

| Modèle | Accuracy | Precision | Recall | F1-score |
|---|---:|---:|---:|---:|
| **Embedding + GlobalAveragePooling1D** | **0.9857** | **0.9716** | **0.9195** | **0.9448** |
| Embedding + LSTM | 0.9659 | 0.9237 | 0.8121 | 0.8643 |
| Transfer Learning (NNLM) | 0.9587 | 0.8601 | 0.8255 | 0.8425 |

### Modèle retenu

Le modèle **Embedding + GlobalAveragePooling1D** est retenu. Il surpasse les deux autres sur toutes les métriques, avec un **F1-score de 0.9448** et un **recall de 0.9195** — soit plus de 9 spams sur 10 correctement détectés.

Le transfer learning (NNLM) est moins performant sur ce dataset : le modèle pré-entraîné sur Google News ne s’adapte pas idéalement au langage SMS (abréviations, fautes, codes). C’est un exemple concret où un modèle simple bien calibré surpasse le transfer learning.

---

## Principaux enseignements

Ce projet met en évidence plusieurs points importants :

- un pipeline simple et bien structuré peut déjà produire de très bons résultats sur un problème de classification de texte court ;
- un modèle plus complexe n’est pas automatiquement meilleur ;
- dans un dataset déséquilibré, l’accuracy seule ne suffit pas ;
- un modèle plus simple peut être préférable lorsqu’il reste plus facile à entraîner, à expliquer et à maintenir.

---

## Interprétation métier

Les résultats obtenus montrent qu’il est possible de détecter efficacement une grande partie des SMS spam à partir du seul texte du message.

D’un point de vue métier, cela signifie qu’un tel modèle peut servir de première brique pour :

- filtrer automatiquement une partie des messages indésirables ;
- réduire l’exposition des utilisateurs à des contenus non souhaités ;
- assister un système plus large de modération ou de protection.

Le modèle retenu ne constitue pas à lui seul une solution industrielle complète, mais il fournit une base solide et cohérente pour un cas d’usage réel.

---

## Structure du dépôt

```text
.
├── data/
│   └── spam.csv
├── notebooks/
│   └── spam_detector.ipynb
├── Bloc 4_Atm_spam_detector_presentation_.pptx
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Technologies utilisées

| Catégorie | Outils |
|---|---|
| Langage | Python 3.12 |
| Manipulation de données | pandas, NumPy |
| Visualisation | Matplotlib |
| Deep Learning | TensorFlow 2.21, Keras, tf_keras |
| Transfer Learning | TensorFlow Hub 0.16, NNLM-en-dim50 |
| NLP | Tokenizer Keras, pad_sequences |
| Évaluation | scikit-learn (classification_report, ConfusionMatrixDisplay) |
| Environnement | Jupyter Notebook, PyCharm |
| Versioning | Git, GitHub |

---

## Installation

### 1. Cloner le dépôt

```bash
git clone <URL_DU_DEPOT>
cd atm-spam-detector
```

### 2. Créer un environnement virtuel

Sous Windows :

```bash
python -m venv .venv
.venv\Scripts\activate
```

Sous macOS / Linux :

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

---

## Exécution

Le projet peut être consulté de deux manières.

### Ouvrir le notebook

```text
notebooks/spam_detector.ipynb
```

Exécuter les cellules dans l’ordre.

---

## Notebook

| Notebook | Description |
|---|---|
| `spam_detector.ipynb` | Notebook complet et exécuté — preprocessing, 3 modèles, évaluation, comparaison |

---

## Limites du projet

Le projet présente plusieurs limites qu’il faut reconnaître clairement :

- le modèle utilise uniquement le **texte brut du message** ;
- il ne prend pas en compte de contexte externe comme l’expéditeur, la fréquence ou l’historique utilisateur ;
- le dataset reste de taille modérée ;
- les performances observées dépendent du jeu de données utilisé ;
- une bonne performance sur ce dataset ne garantit pas automatiquement une généralisation parfaite à des données réelles plus variées.

---

## Pistes d’amélioration

Plusieurs améliorations pourraient être envisagées dans une version plus avancée :

- nettoyage textuel plus poussé ;
- test d’embeddings pré-entraînés ;
- ajustement plus fin des hyperparamètres ;
- gestion plus explicite du déséquilibre des classes ;
- expérimentation avec d’autres architectures de NLP ;
- ajout d’une matrice de confusion visualisée ;
- intégration dans une API ou une application de démonstration.

---

## Conclusion

Ce projet montre qu’un pipeline de deep learning simple, bien structuré et correctement évalué permet de construire un détecteur de SMS spam très performant.

Le résultat le plus important : le **modèle le plus simple (Embedding + GAP)** surpasse à la fois le LSTM et le transfer learning. C’est un rappel fondamental — la complexité architecturale n’est pas une fin en soi. Un modèle bien calibré sur des données bien préparées sera toujours le meilleur point de départ.

Avec un **F1-score de 0.9448** et **plus de 9 spams sur 10 détectés**, ce modèle constitue une solution directement utilisable pour protéger les utilisateurs AT&T.
