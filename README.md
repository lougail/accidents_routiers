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

## Lancement rapide avec Docker

### Prérequis

- Docker
- Docker Compose

### Démarrage

```bash
# Cloner le repo
git clone https://github.com/lougail/accidents_routiers.git
cd accidents_routiers

# Copier les fichiers d'environnement
cp .env.api.example .env.api
cp .env.db.example .env.db
cp .env.frontend.example .env.frontend

# Lancer la stack
docker compose up --build
```

L'application est disponible sur :
- Frontend : http://localhost:8501
- API : http://localhost:8000
- Documentation API : http://localhost:8000/docs
- Prometheus : http://localhost:9090
- Grafana : http://localhost:3000 (admin/admin)
- Alertmanager : http://localhost:9093

### Commandes utiles

```bash
# Lancer en arrière-plan
docker compose up -d

# Voir les logs
docker compose logs -f

# Arrêter la stack
docker compose down

# Arrêter et supprimer les volumes (reset BDD)
docker compose down -v
```

### Images GHCR

```bash
docker pull ghcr.io/lougail/accidents_routiers/api:latest
docker pull ghcr.io/lougail/accidents_routiers/frontend:latest
```

## Structure du projet

```
accidents_routiers/
├── .github/workflows/          # CI/CD (ci, build, release, sync-develop)
├── api/                        # API FastAPI
│   ├── Dockerfile
│   ├── main.py
│   ├── routes.py               # Endpoints (health, predict, feature-importances)
│   ├── state.py                # État global (modèles, metadata)
│   ├── metrics.py              # Métriques Prometheus custom
│   ├── schemas.py
│   ├── model.py
│   └── database.py             # Connexion PostgreSQL
├── frontend/                   # Interface Streamlit
│   ├── Dockerfile
│   ├── app.py
│   ├── pages/
│   └── utils/
├── tests/                      # Tests pytest (API)
├── models/                     # Modèles entraînés (.joblib)
├── notebooks/                  # Pipeline d'analyse (01 à 05)
├── prometheus/                 # Configuration monitoring
│   ├── prometheus.yml          # Scrape config (API, node-exporter, cAdvisor)
│   ├── alert_rules.yml         # 5 règles d'alerte
│   └── alertmanager.yml        # Config Alertmanager
├── grafana/dashboards/         # 4 dashboards JSON exportés
├── docs/                       # Documentation
│   ├── rendus/                 # Livrables projet
│   ├── VEILLE_OBSERVABILITE.md # Concepts monitoring & observabilité
│   ├── DASHBOARD_DESIGN.md     # Design des dashboards Grafana
│   ├── RAPPORT_STRESS_TEST.md  # Résultats stress tests (20/100/200 users)
│   └── EXERCICES_PROMQL.md     # 6 requêtes PromQL commentées
├── scripts/                    # Scripts utilitaires
├── locustfile.py               # Stress testing Locust
├── docker-compose.yml          # 8 services Docker
├── pyproject.toml              # Config projet, dépendances, outils
└── uv.lock
```

L'architecture est composée de 8 services Docker (API FastAPI, Frontend Streamlit, PostgreSQL, Prometheus, Grafana, Alertmanager, Node Exporter, cAdvisor) reliés par un réseau interne.

Les variables d'environnement sont configurées via les fichiers `.env.*`. Des fichiers `.env.*.example` sont fournis comme modèles.

## Installation locale (sans Docker)

```bash
uv sync --group api --group frontend

# Terminal 1 : API
uv run uvicorn api.main:app --reload

# Terminal 2 : Frontend
uv run streamlit run frontend/app.py
```

## Pipeline de notebooks

```
01_exploration → 02a_preparation → 03a_features → 04a_dataset_UC1 → 05a_model_UC1
```

| Notebook | Rôle | Output |
|----------|------|--------|
| 01_exploration | Exploration des données BAAC, choix de la target | Compréhension des données |
| 02a_preparation | Fusion des 4 années, nettoyage | `dataset_complet_raw.csv` |
| 03a_features | Feature engineering | `dataset_features_intelligentes.csv` |
| 04a_dataset_UC1 | Datasets progressifs V1-V4 | `UC1_v1_base.csv` ... `UC1_v4_collision.csv` |
| 05a_model_UC1 | Entraînement CatBoost, évaluation, seuil | Modèles `.joblib` |

## Données

Les fichiers CSV BAAC ne sont pas inclus dans le repo (782 Mo). Pour les obtenir :

1. Télécharger les 4 années (2021-2024) depuis [data.gouv.fr](https://www.data.gouv.fr/fr/datasets/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere/)
2. Placer les fichiers dans `data/<année>/`
3. Exécuter les notebooks dans l'ordre

208 616 accidents en France métropolitaine, dont 35.4% classés graves.

## API — Endpoints

### `GET /health`

```json
{
  "status": "ok",
  "models_loaded": ["v1_base", "v2_route", "v3_vehicules", "v4_collision"],
  "n_models": 4,
  "threshold": 0.45
}
```

### `POST /predict`

```json
{
  "departement": "75",
  "heure": 3,
  "mois": 11,
  "jour_semaine": 5,
  "luminosite": "nuit_non_eclairee"
}
```

### `GET /feature-importances`

Retourne le top 15 des features les plus importantes par modèle.

## Monitoring & Observabilité

Stack de monitoring complète basée sur Prometheus + Grafana :

- **Instrumentation** : `prometheus-client` + `prometheus-fastapi-instrumentator` exposent les métriques sur `/metrics`
- **Métriques custom** : `predictions_total`, `predictions_graves_total`, `prediction_duration_seconds`, `models_loaded`
- **4 dashboards Grafana** : HTTP Overview, Predictions & Performance, Database Performance, RED Metrics par Endpoint
- **5 alertes Prometheus** : taux d'erreur, latence P95, CPU, modèles chargés, API down
- **Stress tests Locust** : 20/100/200 utilisateurs simultanés, 0% erreurs, 158 req/s max

### Stress test (résumé)

| Users | RPS | Failures | P95 |
|-------|-----|----------|-----|
| 20 | 15.8 | 0% | 30ms |
| 100 | 79.8 | 0% | 27ms |
| 200 | 158.5 | 0% | 24ms |

## Choix techniques

- **CatBoost** : gestion native des variables catégorielles, robuste au surapprentissage
- **Split temporel** : entraînement 2021-2023, test 2024
- **Seuil 0.45** : optimisé pour recall > 80%
- **4 modèles progressifs** : adaptés au niveau d'information disponible
- **PostgreSQL** : persistance des prédictions pour analyse ultérieure
- **Prometheus + Grafana** : monitoring temps réel avec alerting
