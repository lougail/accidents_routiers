# Accidents Routiers — UC1 Priorisation des Secours

Classification binaire (grave / non grave) des accidents routiers a partir des donnees BAAC 2021-2024, exposee via API FastAPI + interface Streamlit.

**Stack** : Python 3.13, FastAPI, Streamlit, CatBoost, PostgreSQL, Docker, uv

## Commandes

```bash
# Linting + formatting
uv run ruff check . --fix
uv run ruff format .

# Type checking
uv run mypy api/

# Tests
uv run pytest tests/

# Pre-commit (tous les hooks)
pre-commit run --all-files

# Docker
docker compose up --build        # stack complete
docker compose down -v            # arret + reset BDD
```

## Structure

| Dossier | Role |
|---------|------|
| `api/` | API FastAPI (main, schemas, model, database) |
| `frontend/` | Interface Streamlit (app, pages, utils) |
| `tests/` | Tests pytest pour l'API |
| `models/` | 4 modeles CatBoost `.joblib` + metadata JSON |
| `notebooks/` | Pipeline d'analyse (01 a 05) |
| `data/` | Datasets CSV (non versiones, 782 Mo) |
| `docs/rendus/` | Livrables projet en markdown |
| `.github/workflows/` | CI: ci.yml, build.yml, release.yml, sync-develop.yml |

## Conventions

- **Formatter** : ruff, double quotes, line-length 88, indent spaces
- **Linter** : ruff (F, E, W, I, B, C4, UP, SIM, S, PT, RUF)
- **Type checker** : mypy strict sur `api/`
- **Commits** : conventionnels (`feat:`, `fix:`, `chore:`, `docs:`, etc.)
- **Branches** : feature → develop → master
- **Pre-commit** : trailing-whitespace, ruff, ruff-format, mypy

## CI/CD

- **ci.yml** : lint + tests sur push/PR
- **build.yml** : build et push images Docker vers GHCR
- **release.yml** : semantic-release sur master (bump version, changelog, tag)
- **sync-develop.yml** : sync develop apres release

Images : `ghcr.io/lougail/accidents_routiers/{api,frontend}:latest`

## Modeles ML

4 versions progressives CatBoost, adaptees au niveau d'info disponible lors de l'appel :

| Version | Features | Description |
|---------|----------|-------------|
| V1 | 8 | Lieu + heure |
| V2 | 23 | + caracteristiques route |
| V3 | 32 | + vehicules |
| V4 | 37 | + type collision |

- **Seuil** : 0.45 (optimise pour recall > 80%)
- **Split temporel** : train 2021-2023, test 2024
- **Dependances** : `pyproject.toml` (groups: api, frontend, dev, ml)
