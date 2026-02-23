"""Chargement des modèles et construction des features.

Ce module isole la logique ML du framework web (pas d'import FastAPI).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING

import joblib
import pandas as pd

if TYPE_CHECKING:
    from api.schemas import AccidentInput

logger = logging.getLogger(__name__)

DEFAULT_THRESHOLD = 0.45

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"

VERSIONS = ("v1_base", "v2_route", "v3_vehicules", "v4_collision")


def load_all_models() -> tuple[dict, dict, dict]:
    """Charge les 4 modèles CatBoost et les métadonnées.

    Returns:
        (models, metadata, dep_mapping)
    """
    meta_path = MODELS_DIR / "metadata_UC1_api.json"
    if not meta_path.exists():
        logger.error(
            "Fichier %s introuvable. Exécutez d'abord le notebook 05a.", meta_path
        )
        return {}, {}, {}

    with open(meta_path) as f:
        metadata = json.load(f)

    dep_mapping = metadata.get("dep_mapping", {})

    models = {}
    for version in VERSIONS:
        model_path = MODELS_DIR / f"model_UC1_{version}.joblib"
        if model_path.exists():
            models[version] = joblib.load(model_path)
            n_feat = metadata.get("models", {}).get(version, {}).get("n_features", "?")
            logger.info("Modèle chargé : %s (%s features)", version, n_feat)
        else:
            logger.warning("Fichier %s introuvable", model_path)

    logger.info(
        "%d modèle(s) chargé(s), seuil = %s",
        len(models),
        metadata.get("threshold", DEFAULT_THRESHOLD),
    )
    return models, metadata, dep_mapping


def detect_version(data: AccidentInput) -> str:
    """Détecte le modèle à utiliser selon les champs renseignés."""
    if data.type_collision is not None:
        return "v4_collision"
    if data.nb_vehicules is not None or data.types_vehicules is not None:
        return "v3_vehicules"
    if (
        data.vma is not None
        or data.type_route is not None
        or data.en_agglomeration is not None
    ):
        return "v2_route"
    return "v1_base"


def build_features(
    data: AccidentInput, version: str, metadata: dict, dep_mapping: dict
) -> pd.DataFrame:
    """Transforme les inputs bruts en DataFrame de features pour le modèle."""
    f: dict = {}

    # --- V1 : quand et où ---
    f["dep"] = int(dep_mapping.get(str(data.departement), 0))
    f["heure"] = data.heure
    f["mois"] = data.mois
    f["weekend"] = int(data.jour_semaine >= 5)
    nuit = data.luminosite in ("nuit_eclairee", "nuit_non_eclairee")
    f["nuit"] = int(nuit)
    f["heure_pointe"] = int(data.heure in (7, 8, 9, 17, 18, 19))
    f["heure_danger"] = int(2 <= data.heure <= 6)
    f["nuit_eclairee"] = int(data.luminosite == "nuit_eclairee")

    nuit_non_eclairee = data.luminosite == "nuit_non_eclairee"

    if version in ("v2_route", "v3_vehicules", "v4_collision"):
        # --- V2 : caractéristiques route ---
        vma = data.vma if data.vma is not None else 50
        f["vma"] = vma
        f["nbv"] = data.nbv if data.nbv is not None else 2

        hors_agglo = (
            not data.en_agglomeration if data.en_agglomeration is not None else False
        )
        f["hors_agglo"] = int(hors_agglo)

        bidirect = data.bidirectionnelle if data.bidirectionnelle is not None else False
        f["bidirectionnelle"] = int(bidirect)

        haute_vitesse = vma >= 90
        f["haute_vitesse"] = int(haute_vitesse)
        f["meteo_degradee"] = int(data.meteo_degradee or False)
        f["surface_glissante"] = int(data.surface_glissante or False)
        f["intersection_complexe"] = int(data.intersection or False)
        f["route_en_pente"] = int(data.route_en_pente or False)

        tr = data.type_route or "autre"
        f["route_autoroute"] = int(tr == "autoroute")
        f["route_departementale"] = int(tr == "departementale")
        f["route_communale"] = int(tr == "communale")

        f["nuit_hors_agglo"] = int(nuit_non_eclairee and hors_agglo)
        f["weekend_nuit"] = f["weekend"] * f["nuit"]
        f["vitesse_x_bidirect"] = int(haute_vitesse and bidirect)

    if version in ("v3_vehicules", "v4_collision"):
        # --- V3 : véhicules ---
        vehs = set(data.types_vehicules or [])
        f["has_moto"] = int("moto" in vehs)
        f["has_velo"] = int("velo" in vehs)
        f["has_edp"] = int("edp" in vehs)
        f["has_cyclomoteur"] = int("cyclomoteur" in vehs)
        f["has_pieton"] = int("pieton" in vehs)

        has_lourd = "poids_lourd" in vehs
        f["has_vehicule_lourd"] = int(has_lourd)

        has_vulnerable = any(
            f.get(k, 0)
            for k in (
                "has_moto",
                "has_velo",
                "has_edp",
                "has_cyclomoteur",
                "has_pieton",
            )
        )
        f["collision_asymetrique"] = int(has_lourd and has_vulnerable)
        f["nb_vehicules"] = data.nb_vehicules if data.nb_vehicules is not None else 1

        f["moto_x_hors_agglo"] = f["has_moto"] * f.get("hors_agglo", 0)

    if version == "v4_collision":
        # --- V4 : collision ---
        col = data.type_collision or ""
        f["collision_frontale"] = int(col == "frontale")
        f["collision_arriere"] = int(col == "arriere")
        f["collision_cote"] = int(col == "cote")
        f["collision_solo"] = int(col == "solo")

        f["frontale_x_hors_agglo"] = f["collision_frontale"] * f.get("hors_agglo", 0)

    # Construire le DataFrame dans l'ordre attendu par le modèle
    expected = metadata["models"][version]["features"]
    row = {feat: f.get(feat, 0) for feat in expected}
    df = pd.DataFrame([row])
    df["dep"] = df["dep"].astype("category")
    return df
