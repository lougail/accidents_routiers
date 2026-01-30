# UC1 — Priorisation des Secours

Prédiction de la gravité des accidents routiers pour optimiser l'envoi de moyens de secours.

A partir des données BAAC (Bulletin d'Analyse des Accidents Corporels) 2021-2024, le projet entraîne des modèles de classification binaire (grave / non grave) et les expose via une API REST + une interface Streamlit.

## Résultats

| Modèle | Features | ROC-AUC | Recall | Precision |
|--------|----------|---------|--------|-----------|
| V1 — Lieu/Heure | 8 | 0.737 | 0.809 | 0.497 |
| V2 — + Route | 23 | 0.790 | 0.787 | 0.561 |
| V3 — + Véhicules | 32 | 0.812 | 0.810 | 0.577 |
| V4 — + Collision | 37 | 0.818 | 0.813 | 0.583 |

4 modèles CatBoost entraînés, un par niveau d'information disponible lors de l'appel d'urgence. L'API sélectionne automatiquement le modèle adapté aux données fournies.

## Pipeline de notebooks

```
01_exploration → 02a_preparation → 03a_features → 04a_dataset_UC1 → 05a_model_UC1
```

| Notebook | Rôle | Output |
|----------|------|--------|
| 01_exploration | Exploration des données BAAC, choix de la target | Compréhension des données |
| 02a_preparation | Fusion des 4 années, nettoyage | `dataset_complet_raw.csv` |
| 02b_analyse (optionnel) | Analyse exploratoire, baselines, feature importance | Insights pour 03a |
| 03a_features | Feature engineering | `dataset_features_intelligentes.csv` |
| 04a_dataset_UC1 | Datasets progressifs V1-V4 | `UC1_v1_base.csv` ... `UC1_v4_collision.csv` |
| 05a_model_UC1 | Entraînement CatBoost, évaluation, seuil | Modèles `.joblib` + `metadata_UC1_api.json` |

## Structure du projet

```
accidents_routiers/
├── notebooks/                  # Pipeline d'analyse (5 notebooks)
│   ├── 01_exploration/
│   ├── 02_analyse_baseline/    # 02a (pipeline) + 02b (optionnel)
│   ├── 03_feature_engineering/
│   ├── 04_datasets/
│   └── 05_modelisation/
├── api/                        # API FastAPI
│   ├── main.py                 # Endpoints (health, predict, feature-importances)
│   ├── schemas.py              # Schémas Pydantic (validation entrées/sorties)
│   └── model.py                # Chargement modèles + feature engineering
├── frontend/                   # Interface Streamlit
│   ├── app.py                  # Entrypoint (navigation multipage)
│   ├── pages/
│   │   ├── prediction.py       # Formulaire de prédiction + jauge
│   │   └── dashboard.py        # Visualisations et statistiques
│   └── utils/
│       ├── config.py           # Constantes partagées
│       └── data.py             # Chargement données (cache)
├── models/                     # Modèles entraînés (.joblib) + métadonnées
└── requirements.txt
```

## Installation

```bash
git clone <repo-url>
cd accidents_routiers
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Données

Les fichiers CSV BAAC ne sont pas inclus dans le repo (782 Mo). Pour les obtenir :

1. Télécharger les 4 années (2021-2024) depuis [data.gouv.fr](https://www.data.gouv.fr/fr/datasets/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere/)
2. Placer les fichiers dans `données/<année>/` (ex: `données/2021/carcteristiques-2021.csv`)
3. Exécuter les notebooks dans l'ordre pour générer les datasets intermédiaires

208 616 accidents en France métropolitaine, dont 35.4% classés graves (hospitalisation ou décès).

## Lancement

### 1. Générer les modèles (si pas déjà fait)

Les modèles pré-entraînés sont inclus dans `models/`. Pour les régénérer, télécharger les données BAAC puis exécuter les notebooks dans l'ordre : `01` → `02a` → `03a` → `04a` → `05a`.

### 2. Lancer l'API

```bash
uvicorn api.main:app --reload
```

L'API est disponible sur http://localhost:8000 (documentation Swagger sur `/docs`).

### 3. Lancer le frontend

```bash
streamlit run frontend/app.py
```

L'interface est disponible sur http://localhost:8501.

## API — Endpoints

### `GET /health`

Vérifie que l'API et les modèles sont opérationnels.

```json
{
  "status": "ok",
  "models_loaded": ["v1_base", "v2_route", "v3_vehicules", "v4_collision"],
  "n_models": 4,
  "threshold": 0.45
}
```

### `POST /predict`

Prédit la gravité d'un accident. Le modèle est sélectionné automatiquement selon les champs renseignés.

**Requête minimale (V1)** — seuls lieu et heure :
```json
{
  "departement": "75",
  "heure": 3,
  "mois": 11,
  "jour_semaine": 5,
  "luminosite": "nuit_non_eclairee"
}
```

**Requête complète (V4)** — toutes les informations :
```json
{
  "departement": "75",
  "heure": 3,
  "mois": 11,
  "jour_semaine": 5,
  "luminosite": "nuit_non_eclairee",
  "vma": 90,
  "type_route": "departementale",
  "en_agglomeration": false,
  "nb_vehicules": 2,
  "types_vehicules": ["moto"],
  "type_collision": "frontale"
}
```

**Réponse :**
```json
{
  "prediction": 1,
  "probabilite": 0.7548,
  "grave": true,
  "seuil": 0.45,
  "version_modele": "v4_collision",
  "n_features": 37,
  "metriques_modele": {"roc_auc": 0.818, "recall_at_threshold": 0.813}
}
```

### `GET /feature-importances`

Retourne le top 15 des features les plus importantes pour chaque modèle.

## Choix techniques

- **CatBoost** pour tous les modèles : gestion native des variables catégorielles (`dep`), robuste au surapprentissage
- **Split temporel** : entraînement sur 2021-2023, test sur 2024 (évaluation réaliste)
- **Seuil 0.45** : optimisé pour maximiser le recall (objectif > 80%) tout en limitant les fausses alertes
- **4 modèles progressifs** : chaque modèle est optimisé pour son niveau d'information, plutôt qu'un seul modèle avec des features manquantes mises à 0
