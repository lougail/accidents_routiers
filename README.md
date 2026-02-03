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

### Images DockerHub

```bash
docker pull louisgaillard94/uc1-api:v1
docker pull louisgaillard94/uc1-frontend:v1
```

## Structure du projet

```
accidents_routiers/
├── api/                        # API FastAPI
│   ├── Dockerfile
│   ├── main.py
│   ├── schemas.py
│   ├── model.py
│   ├── database.py             # Connexion PostgreSQL
│   └── requirements.txt
├── frontend/                   # Interface Streamlit
│   ├── Dockerfile
│   ├── app.py
│   ├── pages/
│   │   ├── prediction.py
│   │   └── dashboard.py
│   └── requirements.txt
├── models/                     # Modèles entraînés (.joblib)
├── notebooks/                  # Pipeline d'analyse
├── docker-compose.yml          # Orchestration des services
├── .env.api.example            # Variables API
├── .env.db.example             # Variables PostgreSQL
├── .env.frontend.example       # Variables frontend
├── .dockerignore
└── README.md
```

## Architecture Docker

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                        │
│                                                          │
│  ┌──────────┐    ┌──────────┐    ┌──────────────────┐  │
│  │ Frontend │───▶│   API    │───▶│   PostgreSQL     │  │
│  │ :8501    │    │  :8000   │    │     :5432        │  │
│  └──────────┘    └──────────┘    └──────────────────┘  │
│                                          │              │
│                                   ┌──────▼──────┐      │
│                                   │   Volume    │      │
│                                   │ (persistance)│      │
│                                   └─────────────┘      │
└─────────────────────────────────────────────────────────┘
```

## Variables d'environnement

Chaque service a son propre fichier `.env` :

### `.env.db` — PostgreSQL

| Variable | Description | Défaut |
|----------|-------------|--------|
| `POSTGRES_USER` | Utilisateur PostgreSQL | `uc1` |
| `POSTGRES_PASSWORD` | Mot de passe PostgreSQL | `uc1password` |
| `POSTGRES_DB` | Nom de la base | `uc1db` |

### `.env.api` — API FastAPI

| Variable | Description | Défaut |
|----------|-------------|--------|
| `DATABASE_URL` | URL de connexion BDD | `postgresql://uc1:uc1password@db:5432/uc1db` |
| `CORS_ORIGINS` | Origines autorisées (séparées par virgule) | `http://localhost:8501,http://frontend:8501` |

### `.env.frontend` — Streamlit

| Variable | Description | Défaut |
|----------|-------------|--------|
| `API_URL` | URL de l'API | `http://api:8000` |

## Installation locale (sans Docker)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Terminal 1 : API
uvicorn api.main:app --reload

# Terminal 2 : Frontend
streamlit run frontend/app.py
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
2. Placer les fichiers dans `données/<année>/`
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

## Choix techniques

- **CatBoost** : gestion native des variables catégorielles, robuste au surapprentissage
- **Split temporel** : entraînement 2021-2023, test 2024
- **Seuil 0.45** : optimisé pour recall > 80%
- **4 modèles progressifs** : adaptés au niveau d'information disponible
- **PostgreSQL** : persistance des prédictions pour analyse ultérieure
