# Plan du Projet - Prédiction de la gravité des accidents routiers

## Objectif
Prédire si un accident routier sera **mortel** ou **grave** à partir des données BAAC (2021-2024).

---

## Données de référence (découvertes 01_exploration)

| Métrique | Valeur |
|----------|--------|
| **Total accidents** | 221,044 (4 ans) |
| **Accidents par an** | ~55,000 (stable) |
| **Usagers impliqués** | 506,886 |
| **GPS invalides** | 12,590 (5.7%) → à filtrer |
| **Taux mortel** | 5.8% (12,798 accidents) |
| **Taux grave** | 35.7% (78,907 accidents) |
| **Ratio mortel** | 1:16 → **SMOTE requis** |
| **Ratio grave** | 1:1.8 → EasyEnsemble ou class_weight |

### Points d'attention techniques
- **2022** : Colonne `Accident_Id` à renommer en `Num_Acc`
- **LIEUX** : ~30% des accidents ont plusieurs entrées (intersections) → garder VMA max
- **GPS** : Format string avec virgule → convertir en float

---

## Workflow

### Phase 1 : Analyse Baseline - TERMINE

Comprendre les données et identifier les features importantes.

| Notebook | Description |
|----------|-------------|
| `01_exploration.ipynb` | Exploration des 4 années, stats de référence |
| `02a_preparation_complete.ipynb` | Fusion 4 tables x 4 années, features dérivées |
| `02b_analyse_exploratoire.ipynb` | EDA complet : distributions, corrélations, patterns |
| `02c_feature_importance.ipynb` | Modèle baseline + importance des features |

Scores baseline :

| Target | Modèle | ROC-AUC | Precision | Recall | F1 |
|--------|--------|---------|-----------|--------|-----|
| MORTEL | RF | 0.827 | 15% | 74% | 0.25 |
| GRAVE | RF | 0.811 | 64% | 69% | 0.67 |

UC1 (MORTEL) : Precision de 15% = 85% faux positifs → SMOTE requis

Livrables :
- `dataset_complet_raw.csv` (208,616 x 51, avec Num_Acc)
- `dataset_complet_encoded.csv` (208,616 x ~210)

Décision TARGET :
- UC1 Secours → MORTEL (5.7%, ratio 1:16) → SMOTE
- UC2 Epidemio → GRAVE (35.4%, ratio 1:1.8) → EasyEnsemble

---

### Phase 2 : Feature Engineering - TERMINE

30 features métier créées sur 208k accidents.

| Catégorie | Features | Description |
|-----------|----------|-------------|
| Contexte (5) | `hors_agglo`, `nuit_non_eclairee`, `nuit_eclairee`, `bidirectionnelle`, `haute_vitesse` | Circonstances de l'accident |
| Route (5) | `route_autoroute`, `route_nationale`, `route_departementale`, `route_communale`, `route_rapide` | Type de voie |
| Collision (4) | `collision_frontale`, `collision_arriere`, `collision_cote`, `collision_solo` | Type d'impact |
| Obstacles (3) | `obstacle_arbre`, `obstacle_fixe_dur`, `obstacle_pieton` | Obstacles impliqués |
| Véhicules (10) | `has_moto`, `has_velo`, `has_edp`, `has_cyclomoteur`, `has_pieton`, `has_vulnerable`, `has_poids_lourd`, `has_bus`, `has_vehicule_lourd`, `collision_asymetrique` | Types de véhicules |
| Temporelles (3) | `heure_danger`, `weekend_nuit`, `nuit_hors_agglo` | Patterns temporels validés |

Livrable : `dataset_features_intelligentes.csv` (208,616 x 50 colonnes)

---

### Phase 3 : Création des Datasets par Use Case - TERMINE

#### UC1 : Aide aux Secours (temps réel) - Target MORTEL

| Dataset | Features | Corr max | Description |
|---------|----------|----------|-------------|
| `UC1_v1_base.csv` | 11 | 0.107 | GPS + heure + temporel + jour/nuit |
| `UC1_v2_route.csv` | 23 | 0.153 | + route identifiée (+43% prédictivité) |
| `UC1_v3_vehicules.csv` | 34 | 0.153 | + véhicules décrits |
| `UC1_v4_collision.csv` | 38 | 0.153 | + type collision |

Découverte clé : le saut V1→V2 apporte +43% de pouvoir prédictif. Question prioritaire aux secours : "Où êtes-vous ?" (ville vs route)

#### UC2 : Étude Épidémiologique - Target GRAVE

Deux granularités testées (accident-level et usager-level). Découvertes :
- `ceinture` = feature #1 du dataset usager (-0.223)
- `casque` (+0.195) = paradoxe de Simpson (proxy "deux-roues")
- Conducteurs sans ceinture : 27.2% vs avec ceinture 9.7% → effet protecteur 2.8x

---

### Phase 4 : Modélisation - UC1 TERMINE, UC2 non réalisé

#### UC1 - MORTEL (Priorisation Secours)

| Dataset | Modèle | ROC-AUC | Recall | F1 |
|---------|--------|---------|--------|-----|
| v1_base | LogReg | 0.647 | 0.558 | 0.158 |
| v2_route | LogReg | 0.739 | 0.661 | 0.215 |
| v3_vehicules | LogReg | 0.764 | 0.691 | 0.220 |
| v4_collision | LogReg | 0.779 | 0.696 | 0.225 |
| v4_collision | RF | 0.792 | 0.234 | 0.225 |
| v4_collision | ExtraTrees | 0.793 | 0.686 | 0.246 |
| v4_collision | XGBoost | 0.810 | 0.756 | 0.239 |
| v4_collision | LightGBM | 0.814 | 0.762 | 0.244 |
| v4_collision | CatBoost | 0.801 | 0.694 | 0.248 |
| **FINAL optimisé** | **LightGBM** | **0.814** | **0.762** | **0.244** |

Note : avec seuil 0.3, Recall = 0.895 (90% des mortels détectés)

#### UC2 - GRAVE (Épidémiologie) - Non réalisé

Modélisation UC2 non faite, pas prioritaire pour le livrable API/Frontend.

Livrables Phase 4 :
- `models/model_UC1_final.joblib` - Modèle pour l'API
- `models/feature_names_UC1.json` - Features attendues par l'API
- Graphiques UC1 sauvegardés dans `models/`

---

### Phase 5-6 : API, Frontend, CI/CD - TERMINE

- API FastAPI avec 4 modèles CatBoost (V1-V4), sélection automatique
- Frontend Streamlit (prédiction + dashboard)
- Docker Compose (API + Frontend + PostgreSQL)
- CI/CD GitHub Actions (lint, type-check, tests, build Docker, release)
- Images publiées sur DockerHub

---

## Insights clés

1. **Nuit avec éclairage** (lum=5) plus sûr que le jour (3.16% vs 5.24%)
2. **Autoroute moins mortelle** que départementale (4.34% vs 9.47%)
3. **Arbre = obstacle le plus mortel** (20.34% mortalité)
4. **Plus de véhicules = moins grave** (embouteillages = vitesse réduite ?)

---

## Pistes d'amélioration

- Modélisation UC2 (target GRAVE, épidémiologie)
- Features géographiques : clustering des zones à risque
- SHAP values pour l'interprétabilité
- Calibration des probabilités (CalibratedClassifierCV)
- MLflow pour le tracking des expériences
