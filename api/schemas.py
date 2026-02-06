"""Schémas Pydantic pour la validation des requêtes et réponses."""

from typing import Literal

from pydantic import BaseModel, Field


class AccidentInput(BaseModel):
    """Caractéristiques d'un accident pour la prédiction de gravité."""

    # Section 1 — Quand et où (toujours requis)
    departement: str = Field(..., description="Code département ('75', '13', '2A'...)")
    heure: int = Field(..., ge=0, le=23, description="Heure (0-23)")
    mois: int = Field(..., ge=1, le=12, description="Mois (1-12)")
    jour_semaine: int = Field(..., ge=0, le=6, description="0=Lundi, 6=Dimanche")
    luminosite: Literal["jour", "nuit_eclairee", "nuit_non_eclairee"] = Field(
        ..., description="'jour' | 'nuit_eclairee' | 'nuit_non_eclairee'"
    )

    # Section 2 — Route (optionnel → active V2)
    vma: int | None = Field(
        None, ge=20, le=130, description="Vitesse max autorisée (km/h)"
    )
    nbv: int | None = Field(None, ge=1, le=10, description="Nombre de voies")
    type_route: Literal["autoroute", "departementale", "communale", "autre"] | None = (
        Field(
            None,
            description="'autoroute' | 'departementale' | 'communale' |'autre'",
        )
    )
    en_agglomeration: bool | None = Field(None)
    bidirectionnelle: bool | None = Field(None)
    meteo_degradee: bool | None = Field(None)
    surface_glissante: bool | None = Field(None)
    intersection: bool | None = Field(None)
    route_en_pente: bool | None = Field(None)

    # Section 3 — Véhicules (optionnel → active V3)
    nb_vehicules: int | None = Field(None, ge=1, description="Nombre de véhicules")
    types_vehicules: list[
        Literal["moto", "velo", "edp", "cyclomoteur", "pieton", "poids_lourd"]
    ] | None = Field(
        None,
        description="'moto','velo','edp','cyclomoteur','pieton','poids_lourd'",
    )

    # Section 4 — Collision (optionnel → active V4)
    type_collision: Literal["frontale", "arriere", "cote", "solo"] | None = Field(
        None,
        description="'frontale' | 'arriere' | 'cote' | 'solo'",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "departement": "75",
                    "heure": 22,
                    "mois": 11,
                    "jour_semaine": 5,
                    "luminosite": "nuit_eclairee",
                    "vma": 50,
                    "type_route": "communale",
                    "en_agglomeration": True,
                    "nb_vehicules": 2,
                    "types_vehicules": ["moto"],
                    "type_collision": "cote",
                }
            ]
        }
    }


class PredictionResponse(BaseModel):
    """Résultat de la prédiction de gravité."""

    prediction: int = Field(..., description="1 = grave, 0 = non grave")
    probabilite: float = Field(..., ge=0, le=1, description="Probabilité de gravité")
    grave: bool
    seuil: float
    version_modele: str = Field(
        ..., description="v1_base | v2_route | v3_vehicules | v4_collision"
    )
    n_features: int
    metriques_modele: dict


class HealthResponse(BaseModel):
    """Statut de l'API."""

    status: str
    models_loaded: list[str]
    n_models: int
    threshold: float
