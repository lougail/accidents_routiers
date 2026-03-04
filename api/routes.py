import time

from fastapi import APIRouter, HTTPException

from api import state
from api.database import save_prediction
from api.metrics import (
    http_errors_total,
    prediction_duration_seconds,
    predictions_graves_total,
    predictions_total,
)
from api.model import DEFAULT_THRESHOLD, build_features, detect_version
from api.schemas import AccidentInput, HealthResponse, PredictionResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Vérifie que l'API et les modèles sont opérationnels."""
    return HealthResponse(
        status="ok" if state.models else "no_models",
        models_loaded=list(state.models.keys()),
        n_models=len(state.models),
        threshold=state.metadata.get("threshold", DEFAULT_THRESHOLD),
    )


@router.post("/predict", response_model=PredictionResponse)
def predict(data: AccidentInput) -> PredictionResponse:
    """Prédit la gravité d'un accident.

    Le modèle est sélectionné automatiquement selon les champs renseignés :
    - V1 (lieu/heure) si seuls les champs obligatoires sont fournis
    - V2 (+route) si les infos route sont ajoutées
    - V3 (+véhicules) si les véhicules sont précisés
    - V4 (+collision) si le type de collision est renseigné
    """
    start = time.time()
    if not state.models:
        http_errors_total.labels(type="no_model").inc()
        raise HTTPException(status_code=503, detail="Aucun modèle chargé")

    version = detect_version(data)
    if version not in state.models:
        http_errors_total.labels(type="no_model").inc()
        raise HTTPException(status_code=503, detail=f"Modèle {version} non disponible")

    threshold = state.metadata.get("threshold", DEFAULT_THRESHOLD)
    X = build_features(data, version, state.metadata, state.dep_mapping)
    proba = float(state.models[version].predict_proba(X)[0, 1])
    grave = proba >= threshold

    # Sauvegarde en base de données
    save_prediction(
        input_data=data.model_dump(),
        model_version=version,
        probability=proba,
        prediction=int(grave),
        grave=grave,
    )
    predictions_total.labels(version=version).inc()
    if grave:
        predictions_graves_total.labels(version=version).inc()
    prediction_duration_seconds.labels(version=version).observe(time.time() - start)

    model_info = state.metadata.get("models", {}).get(version, {})
    return PredictionResponse(
        prediction=int(grave),
        probabilite=round(proba, 4),
        grave=grave,
        seuil=threshold,
        version_modele=version,
        n_features=model_info.get("n_features", 0),
        metriques_modele=model_info.get("metrics_test_2024", {}),
    )


@router.get("/feature-importances")
def feature_importances() -> dict[str, list[dict[str, str | float]]]:
    """Retourne le top 15 features par modèle."""
    result: dict[str, list[dict[str, str | float]]] = {}
    for version, model in state.models.items():
        if hasattr(model, "get_feature_importance"):
            importances = model.get_feature_importance()
            features = (
                state.metadata.get("models", {}).get(version, {}).get("features", [])
            )
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
