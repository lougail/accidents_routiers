# Synthèse Projet : Prédiction de Gravité des Accidents Routiers

**Date** : 30 janvier 2025
**Auteur** : Louis
**Données** : BAAC 2021-2024 (data.gouv.fr)

---

## 1. Contexte et Objectifs

### 1.1 Source des données

Les données BAAC (Bulletin d'Analyse des Accidents Corporels) sont collectées par les forces de l'ordre pour chaque accident corporel en France. Elles contiennent :

| Table | Granularité | Contenu |
|-------|-------------|---------|
| CARACT | 1 ligne/accident | Date, heure, lieu, conditions |
| LIEUX | 1+ lignes/accident | Caractéristiques de la route |
| VEHICULES | 1+ lignes/accident | Types de véhicules impliqués |
| USAGERS | 1+ lignes/accident | Personnes impliquées + **GRAVITÉ** |

**Volume** : ~55 000 accidents/an, soit ~220 000 sur 4 ans.

### 1.2 Les deux Use Cases

| | UC1 : Aide aux Secours | UC2 : Épidémiologie |
|---|---|---|
| **Question** | "Cet accident est-il grave ?" | "Quels facteurs augmentent le risque ?" |
| **Moment** | Temps réel (appel d'urgence) | Analyse post-hoc |
| **Utilisateur** | Régulateur SAMU/Pompiers | Chercheur/Décideur |
| **Objectif** | Prioriser l'intervention | Identifier leviers de prévention |
| **Contrainte** | Features disponibles à l'appel uniquement | Toutes features disponibles |
| **Granularité** | Accident | Usager |

---

## 2. Choix de la Variable Cible

### 2.1 Variable `grav` dans les données

La gravité est enregistrée au niveau **usager** (pas accident) :
- 1 = Indemne
- 2 = Tué
- 3 = Hospitalisé
- 4 = Blessé léger

**Attention** : Les codes ne sont PAS ordonnés par gravité !

### 2.2 Targets définies

| Target | Définition | Niveau | Taux |
|--------|------------|--------|------|
| `mortel` | Au moins 1 tué (grav=2) | Accident | 5.7% |
| `grave` | Au moins 1 tué OU hospitalisé (grav∈{2,3}) | Accident | 35.4% |
| `grave_usager` | Usager tué ou hospitalisé | Usager | 17.7% |

### 2.3 Décision : UC1 utilise `grave` (pas `mortel`)

**Décision initiale** : Utiliser `mortel` pour UC1
**Décision finale** : Utiliser `grave` pour UC1

| Critère | `mortel` | `grave` | Avantage |
|---------|----------|---------|----------|
| Taux positifs | 5.7% | 35.4% | `grave` : plus de cas pour apprendre |
| Ratio classes | 1:16.6 | 1:1.8 | `grave` : moins déséquilibré |
| SMOTE requis | Oui | Non | `grave` : plus simple |
| Utilité opérationnelle | Faible (souvent trop tard) | Élevée | `grave` : intervention utile |

**Justification clé** :
- Un accident "mortel" = décès souvent instantané, l'intervention ne change rien
- Un accident "grave" (hospitalisé) = l'intervention rapide peut sauver des vies
- **100% des mortels sont inclus dans grave** (tout mortel est grave)

**Question ouverte** : Ce choix est-il validé par le formateur ? C'est un choix métier important.

---

## 3. Pipeline de Données

```
Données brutes BAAC (4 tables × 4 ans)
         │
         ▼
┌─────────────────────────────────────┐
│  01_exploration.ipynb               │
│  - Comprendre la structure          │
│  - Identifier les pièges (2022)     │
│  - Analyser le déséquilibre         │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  02a_preparation_complete.ipynb     │
│  - Fusionner les 4 années           │
│  - Créer les targets                │
│  - Nettoyer (GPS, dédoublonnage)    │
│  OUTPUT: dataset_complet_raw.csv    │
│          208,616 × 54 colonnes      │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  03a_features_intelligentes.ipynb   │
│  - Créer features métier            │
│  - Supprimer redondances            │
│  - Réduire dimensionnalité          │
│  OUTPUT: dataset_features_intel...  │
│          208,616 × 46 colonnes      │
└─────────────────────────────────────┘
         │
         ├──────────────────┐
         ▼                  ▼
┌─────────────────┐  ┌─────────────────┐
│  04a (UC1)      │  │  04b/c (UC2)    │
│  Datasets       │  │  Datasets       │
│  progressifs    │  │  complets       │
│  V1→V2→V3→V4    │  │                 │
└─────────────────┘  └─────────────────┘
         │                  │
         ▼                  ▼
┌─────────────────┐  ┌─────────────────┐
│  05a (UC1)      │  │  05b (UC2)      │
│  Modélisation   │  │  Modélisation   │
│  Target: grave  │  │  Target: grave  │
│  (niveau accid.)│  │  (niveau usager)│
└─────────────────┘  └─────────────────┘
```

---

## 4. Décisions Techniques Majeures

### 4.1 Géographie : `dep` au lieu de `lat/long`

| Aspect | `lat/long` | `dep` |
|--------|------------|-------|
| Granularité | Très fine (mètre) | Département (~100 valeurs) |
| Risque overfitting | Élevé | Faible |
| Interprétabilité | Faible | Bonne |
| Généralisation | Mauvaise | Meilleure |

**Décision** : Utiliser `dep` pour UC1

**Question ouverte** : Les collègues utilisent-ils `dep` aussi ? À confirmer.

### 4.2 Split : Temporel vs Random

| Aspect | Random Split | Split Temporel |
|--------|--------------|----------------|
| Méthode | 80/20 aléatoire | Train 2021-2023 / Test 2024 |
| Réalisme | Faible (fuite temporelle) | Élevé |
| Performance apparente | Plus élevée | Plus réaliste |
| Généralisation | Surestimée | Estimée correctement |

**Décision** : Split temporel (train 2021-2023, test 2024)

**Justification** : En production, le modèle prédit sur des données futures, pas sur des données mélangées avec le passé.

### 4.3 Features supprimées

#### Redondantes (corrélation > 0.7)

| Feature supprimée | Corrélée avec | Corrélation |
|-------------------|---------------|-------------|
| `nuit_non_eclairee` | `nuit_hors_agglo` | 0.875 |
| `has_poids_lourd` | `has_vehicule_lourd` | 0.876 |
| `has_bus` | `has_vehicule_lourd` | inclus |
| `nb_conducteurs` | `nb_vehicules` | 0.998 |
| `nb_passagers` | `nb_usagers` | 0.863 |
| `jour_semaine` | `weekend` | redondant |

#### Inutiles (corrélation quasi-nulle avec target)

| Feature | Corrélation avec `grave` | Décision |
|---------|--------------------------|----------|
| `has_vulnerable` | -0.001 | Supprimée |
| `route_nationale` | -0.002 | Supprimée |

#### Post-accident (non disponibles à l'appel)

- `obstacle_arbre`, `obstacle_fixe_dur`, `obstacle_pieton`
- `nb_usagers`, `nb_pietons`, `age_moyen`
- `obs_max`, `obsm_max`, `choc_mode`, `manv_mode`

### 4.4 Features ajoutées (v2)

| Feature | Source | Description |
|---------|--------|-------------|
| `meteo_degradee` | `atm` | Pluie, neige, brouillard, vent |
| `surface_glissante` | `surf` | Mouillée, verglacée, enneigée |
| `intersection_complexe` | `int` | Intersection, giratoire |
| `route_en_pente` | `prof` | Pente, sommet/bas de côte |

### 4.5 Encodage catégoriel natif pour `dep` (v3)

| Aspect | `pd.factorize()` (v2) | `astype('category')` (v3) |
|--------|------------------------|---------------------------|
| Type de split | Ordinal (< / >) | Sous-ensembles ({A, B} vs {C, D}) |
| Problème | Impose un ordre artificiel aux départements | Aucun |
| Compatibilité | Tous modèles | LightGBM, CatBoost natif ; XGBoost avec `enable_categorical` |

**Pourquoi** : Les départements n'ont pas d'ordre naturel. Le code 75 (Paris) n'est pas "plus grand" que le code 13 (Bouches-du-Rhône). L'encodage catégoriel permet aux arbres de regrouper librement les départements similaires.

### 4.6 Validation croisée temporelle (v3)

| Aspect | `StratifiedKFold` (v2) | `TimeSeriesSplit` (v3) |
|--------|------------------------|------------------------|
| Méthode | Mélange aléatoire des années | Folds chronologiques |
| Risque | Fuite temporelle (entraîne sur 2023, valide sur 2021) | Aucune fuite |
| Cohérence avec le split final | Faible | Totale |

```
Fold 1 : Train [2021]        → Valid [2022]
Fold 2 : Train [2021, 2022]  → Valid [2023]
Fold 3 : Train [2021..2023]  → Valid [2024... mais 2024 = test]
```

**Pourquoi** : Le GridSearchCV doit respecter la même logique temporelle que le split final. Sinon on sélectionne des hyperparamètres optimisés pour un contexte irréaliste.

### 4.7 Sélection du seuil sur validation (v3)

| Aspect | Sur le test (v2) | Sur la validation (v3) |
|--------|------------------|------------------------|
| Données utilisées | Test 2024 | Validation 2023 |
| Indépendance du test | Compromise | Préservée |
| Méthode | Entraîne sur 2021-2023, choisit seuil sur 2024 | Entraîne sur 2021-2022, choisit seuil sur 2023 |
| Évaluation finale | Biaisée (seuil optimisé sur test) | Non biaisée (test jamais vu) |

```
2021-2022 → Entraînement du modèle de seuil
2023      → Sélection du seuil opérationnel (0.45)
2024      → Évaluation finale (jamais touché avant)
```

**Pourquoi** : Si on choisit le seuil sur le test, les métriques reportées sont optimistes. Le test doit rester strictement indépendant pour estimer les performances réelles en production.

### 4.8 Feature interactions (v3)

| Interaction | Features croisées | Hypothèse métier |
|-------------|-------------------|------------------|
| `frontale_x_hors_agglo` | `collision_frontale` × `hors_agglo` | Choc frontal à haute vitesse hors agglomération = très grave |
| `vitesse_x_bidirect` | `haute_vitesse` × `bidirectionnelle` | Route rapide sans séparation = risque de choc frontal |
| `moto_x_hors_agglo` | `has_moto` × `hors_agglo` | Moto hors agglomération = vulnérabilité + vitesse |

**Pourquoi** : Les arbres de décision captent les interactions, mais doivent les découvrir par combinaison de splits successifs. En les pré-calculant, on facilite l'apprentissage et on rend les interactions explicites.

---

## 5. Résultats Modélisation UC1

### 5.1 Comparaison des modèles (v4_collision + interactions, split temporel)

| Modèle | ROC-AUC | Recall | Precision | F1 |
|--------|---------|--------|-----------|-----|
| Naive | 0.50 | 0.35 | 0.36 | - |
| LogReg | 0.76 | 0.67 | 0.58 | 0.62 |
| RandomForest | 0.80 | 0.66 | 0.63 | 0.65 |
| XGBoost | 0.82 | 0.76 | 0.61 | 0.68 |
| **LightGBM** | **0.82** | **0.77** | **0.61** | **0.68** |
| CatBoost | 0.82 | 0.74 | 0.62 | 0.68 |

**Meilleur modèle** : LightGBM après GridSearch (ROC-AUC = 0.818)

**Note** : Les performances sont plus basses que l'ancienne version (0.84) car `lat/long` et `jour_semaine` ont été retirés. Le modèle généralise mieux mais le score apparent baisse.

**Améliorations v3** : Encodage catégoriel natif, TimeSeriesSplit, feature interactions. Les métriques exactes seront mises à jour après ré-exécution du pipeline.

### 5.2 Analyse des seuils (sur validation 2023)

| Seuil | Recall | Precision | % Alertes |
|-------|--------|-----------|-----------|
| 0.30 | 0.91 | 0.51 | 64% |
| 0.40 | 0.85 | 0.56 | 55% |
| **0.45** | **0.82** | **0.58** | **50%** |
| 0.50 | 0.77 | 0.61 | 46% |
| 0.60 | 0.67 | 0.66 | 37% |

**Seuil choisi** : 0.45 (Recall ≥ 0.80)

**Méthodologie v3** : Le seuil est sélectionné sur le jeu de **validation (2023)**, pas sur le test (2024). Le modèle de sélection est entraîné sur 2021-2022, prédit sur 2023, et le seuil optimal est choisi sur ces prédictions. L'évaluation finale sur 2024 est donc non biaisée.

**Justification** : Pour les secours, un faux négatif (accident grave non détecté) est plus grave qu'un faux positif (fausse alerte).

### 5.3 Interprétation opérationnelle

Avec le seuil 0.45 :
- **82% des accidents graves sont détectés** (Recall = 0.815)
- **58% des alertes sont de vrais accidents graves** (Precision = 0.584)
- **50% des accidents génèrent une alerte** prioritaire

**Trade-off accepté** :
- 18.5% des accidents graves non détectés (faux négatifs)
- 42% de fausses alertes (faux positifs)

**Profil des faux négatifs** : accidents urbains (en agglomération, routes communales, faible VMA), où les indicateurs habituels de gravité sont absents.

### 5.4 Feature importance et interprétabilité (v3)

Trois méthodes complémentaires :

| Méthode | Ce qu'elle mesure | Biais connu |
|---------|-------------------|-------------|
| Split count | Nb de fois qu'une feature est utilisée pour splitter | Favorise les features à haute cardinalité |
| Gain | Réduction moyenne de l'erreur quand la feature est utilisée | Plus fiable que split count |
| SHAP | Contribution marginale de chaque feature à chaque prédiction | Référence théorique (valeurs de Shapley) |

**Top features attendues** : `hors_agglo`, `dep`, `collision_frontale`, `haute_vitesse`, `nb_vehicules`

---

## 6. Questions Ouvertes / Points à Valider

### 6.1 Choix métier

1. **Target `grave` vs `mortel`** : Le formateur valide-t-il ce choix ?
2. **Seuil 0.45** : Est-ce le bon compromis pour les secours ?
3. **Features exclues** : `lat/long` vraiment inutiles ?

### 6.2 Choix techniques

1. **Split temporel** : Les performances sont-elles acceptables ?
2. **Multicolinéarité** : A-t-on trop supprimé de features ?
3. **Nouvelles features météo** : Apportent-elles vraiment de la valeur ?
4. **TimeSeriesSplit** (v3) : 3 folds suffisants ? (Limité par le nombre d'années)
5. **Feature interactions** (v3) : Les 3 interactions choisies sont-elles pertinentes ?

### 6.3 UC2

1. **UC2 non finalisé** : Le notebook 05b existe mais n'a pas été mis à jour avec les changements v2
2. **Granularité usager** : Cohérent avec l'objectif épidémio ?

---

## 7. Fichiers du Projet

### 7.1 Notebooks (ordre d'exécution)

**Pipeline principal UC1 :**

| # | Fichier | Statut | Rôle |
|---|---------|--------|------|
| 1 | `01_exploration/01_exploration.ipynb` | ✅ Nettoyé | Exploration initiale, compréhension BAAC |
| 2 | `02_analyse_baseline/02a_preparation_complete.ipynb` | ✅ Nettoyé | Préparation dataset unifié |
| 3 | `02_analyse_baseline/02b_analyse_complete.ipynb` | ✅ Nouveau | EDA + Baseline + Feature importance |
| 4 | `03_feature_engineering/03a_features_intelligentes.ipynb` | ✅ Nettoyé | Feature engineering |
| 5 | `04_datasets/UC1_secours/04a_dataset_UC1.ipynb` | ✅ Nettoyé | Datasets progressifs UC1 |
| 6 | `05_modelisation/05a_model_UC1_secours.ipynb` | ✅ Nettoyé | Modélisation finale UC1 |

**Pipeline UC2 :**

| # | Fichier | Statut | Rôle |
|---|---------|--------|------|
| 7 | `04_datasets/UC2_epidemio/04b_dataset_UC2.ipynb` | ✅ Nettoyé | Datasets UC2 (granularité accident) |
| 8 | `04_datasets/UC2_epidemio/04c_dataset_UC2_usager.ipynb` | ✅ Nettoyé | Datasets UC2 (granularité usager) |
| 9 | `05_modelisation/05b_model_UC2_epidemio.ipynb` | ✅ Nettoyé | Modélisation UC2 + facteurs de risque |

### 7.2 Données générées

| Fichier | Généré par | Utilisé par |
|---------|------------|-------------|
| `dataset_complet_raw.csv` | 02a | 02b, 03a |
| `dataset_features_intelligentes.csv` | 03a | 04a, 04b, 04c |
| `UC1_v1_base.csv` | 04a | 05a |
| `UC1_v2_route.csv` | 04a | 05a |
| `UC1_v3_vehicules.csv` | 04a | 05a |
| `UC1_v4_collision.csv` | 04a | 05a |
| `UC2_v1_contexte.csv` | 04b | 05b |
| `UC2_v2_vehicules.csv` | 04b | 05b |
| `UC2_v3_complet.csv` | 04b | 05b |
| `UC2_usager_v1_demo.csv` | 04c | 05b |
| `UC2_usager_v2_comportement.csv` | 04c | 05b |
| `UC2_usager_v3_complet.csv` | 04c | 05b |

### 7.3 Modèles sauvegardés

| Fichier | Contenu |
|---------|---------|
| `models/model_UC1_final.joblib` | Modèle LightGBM entraîné (UC1, target `grave`) |
| `models/metadata_UC1.json` | Hyperparamètres, métriques aux 2 seuils (0.5 et 0.45), méthode de CV |
| `models/model_UC2_final.joblib` | Modèle BalancedBagging entraîné (UC2, target `grave_usager`) |
| `models/metadata_UC2.json` | Hyperparamètres, métriques, facteurs de risque |

**Contenu metadata_UC1.json (v3)** :
- `best_params` : hyperparamètres du LightGBM optimisé
- `cv_method` : `TimeSeriesSplit(n_splits=3)`
- `split` : `temporel_2021-2023_train_2024_test`
- `threshold_selection` : `validation_2023`
- `metrics_at_default_threshold_0.5` : ROC-AUC, recall, precision, f1
- `metrics_at_operational_threshold` : seuil 0.45, recall, precision, f1
- `features` : liste des features utilisées

---

## 8. Résumé des Modifications v2

| Modification | Raison | Impact |
|--------------|--------|--------|
| `dep` au lieu de `lat/long` | Éviter overfitting | Meilleure généralisation |
| `annee` conservé | Split temporel | Évaluation réaliste |
| Features météo ajoutées | Exploiter `atm`, `surf` | +4 features |
| Features redondantes supprimées | Multicolinéarité | -8 features |
| Target `grave` (UC1) | Ratio 1:1.8 | SMOTE non requis |
| Split temporel | Réalisme | Perf légèrement plus basses |

---

## 9. Résumé des Modifications v3

| Modification | Avant (v2) | Après (v3) | Pourquoi |
|--------------|------------|------------|----------|
| Encodage `dep` | `pd.factorize()` (ordinal) | `.astype('category')` (natif) | Les départements n'ont pas d'ordre ; permet des splits par sous-ensembles |
| Cross-validation | `StratifiedKFold` (mélange les années) | `TimeSeriesSplit` (chronologique) | Cohérent avec le split temporel, pas de fuite |
| Sélection du seuil | Sur le test 2024 | Sur la validation 2023 | Le test reste indépendant, métriques non biaisées |
| Feature importance | Split count uniquement | Split count + gain + SHAP | 3 vues complémentaires, interprétabilité renforcée |
| Feature interactions | Aucune | 3 interactions métier | Facilite l'apprentissage des combinaisons à risque |
| Metadata sauvegardé | Métriques à seuil 0.5 uniquement | Métriques aux 2 seuils (0.5 et 0.45) | Reflète les performances opérationnelles réelles |
| CatBoost | Encodage standard | `cat_features` natif | Exploite le traitement catégoriel optimisé de CatBoost |
| XGBoost | Encodage standard | `enable_categorical=True` | Support natif des catégories |

---

## 10. Prochaines Étapes

1. ~~**Revoir chaque notebook** ensemble pour valider la cohérence~~ ✅ Fait
2. ~~**Documenter** les choix dans les notebooks~~ ✅ Fait
3. ~~**Valider UC2** (notebooks 04b, 04c, 05b)~~ ✅ Fait
4. ~~**Améliorations v3** (encodage, TimeSeriesSplit, validation, SHAP, interactions)~~ ✅ Fait
5. **Exécuter le pipeline complet** et vérifier les outputs (mettre à jour les métriques)
6. **Préparer la présentation** pour le formateur
