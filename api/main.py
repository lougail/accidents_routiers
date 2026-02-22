"""
UC1 — API de Priorisation des Secours
Prédiction de la gravité des accidents routiers

Endpoints :
  GET  /health              → statut de l'API
  POST /predict             → prédiction de gravité
  GET  /feature-importances → importance des features par modèle

Lancement :
  uvicorn api.main:app --reload
"""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api.database import init_db, save_prediction
from api.model import build_features, detect_version, load_all_models
from api.schemas import AccidentInput, HealthResponse, PredictionResponse

# Origines autorisées pour CORS (configurable via env)
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS", "http://localhost:8501,http://frontend:8501"
).split(",")

# --- État applicatif (chargé au démarrage) ---
models: dict = {}
metadata: dict = {}
dep_mapping: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Charge les modèles au démarrage, libère les ressources à l'arrêt."""
    global models, metadata, dep_mapping
    models, metadata, dep_mapping = load_all_models()
    init_db()
    yield
    models.clear()
    metadata.clear()
    dep_mapping.clear()


app = FastAPI(
    title="UC1 — Priorisation des Secours",
    description="Prédiction de la gravité des accidents routiers",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# --- Endpoints ---


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Vérifie que l'API et les modèles sont opérationnels."""
    return HealthResponse(
        status="ok" if models else "no_models",
        models_loaded=list(models.keys()),
        n_models=len(models),
        threshold=metadata.get("threshold", 0.45),
    )


@app.post("/predict", response_model=PredictionResponse)
def predict(data: AccidentInput) -> PredictionResponse:
    """Prédit la gravité d'un accident.

    Le modèle est sélectionné automatiquement selon les champs renseignés :
    - V1 (lieu/heure) si seuls les champs obligatoires sont fournis
    - V2 (+route) si les infos route sont ajoutées
    - V3 (+véhicules) si les véhicules sont précisés
    - V4 (+collision) si le type de collision est renseigné
    """
    if not models:
        raise HTTPException(status_code=503, detail="Aucun modèle chargé")

    version = detect_version(data)
    if version not in models:
        raise HTTPException(status_code=503, detail=f"Modèle {version} non disponible")

    threshold = metadata.get("threshold", 0.45)
    X = build_features(data, version, metadata, dep_mapping)
    proba = float(models[version].predict_proba(X)[0, 1])
    grave = proba >= threshold

    # Sauvegarde en base de données
    save_prediction(
        input_data=data.model_dump(),
        model_version=version,
        probability=proba,
        prediction=int(grave),
        grave=grave,
    )

    model_info = metadata.get("models", {}).get(version, {})
    return PredictionResponse(
        prediction=int(grave),
        probabilite=round(proba, 4),
        grave=grave,
        seuil=threshold,
        version_modele=version,
        n_features=model_info.get("n_features", 0),
        metriques_modele=model_info.get("metrics_test_2024", {}),
    )


@app.get("/feature-importances")
def feature_importances() -> dict[str, list[dict[str, float]]]:
    """Retourne le top 15 features par modèle."""
    result: dict[str, list[dict[str, float]]] = {}
    for version, model in models.items():
        if hasattr(model, "get_feature_importance"):
            importances = model.get_feature_importance()
            features = metadata["models"][version]["features"]
            pairs = sorted(
                zip(features, importances.tolist(), strict=False),
                key=lambda x: x[1],
                reverse=True,
            )
            result[version] = [
                {"feature": feat, "importance": round(imp, 4)}
                for feat, imp in pairs[:15]
            ]
    return result
