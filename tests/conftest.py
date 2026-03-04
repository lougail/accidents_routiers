"""Fixtures partagées pour les tests."""

from unittest.mock import Mock, patch

import numpy as np
import pytest
from fastapi.testclient import TestClient

import api.main
from api import state


@pytest.fixture
def client():
    """Client de test FastAPI sans modèles chargés.

    Le lifespan charge les modèles au démarrage.
    On les vide ensuite pour tester le comportement sans modèles.
    """
    with TestClient(api.main.app, raise_server_exceptions=False) as c:
        state.models.clear()
        state.metadata.clear()
        state.dep_mapping.clear()
        yield c


@pytest.fixture
def client_with_model():
    """Client de test avec un faux modèle V1.

    - Mock du modèle : predict_proba renvoie [[0.25, 0.75]] (75% gravité)
    - Mock de save_prediction : ne fait rien (pas de DB en test)
    - Métadonnées minimales pour que build_features fonctionne
    """
    with TestClient(api.main.app, raise_server_exceptions=False) as c:
        # Faux modèle qui simule predict_proba
        fake_model = Mock()
        fake_model.predict_proba.return_value = np.array([[0.25, 0.75]])

        # Injecter le faux modèle
        state.models.clear()
        state.models["v1_base"] = fake_model

        # Métadonnées minimales (liste de features attendues par build_features)
        state.metadata.clear()
        state.metadata["threshold"] = 0.45
        state.metadata["models"] = {
            "v1_base": {
                "features": [
                    "dep",
                    "heure",
                    "mois",
                    "weekend",
                    "nuit",
                    "heure_pointe",
                    "heure_danger",
                    "nuit_eclairee",
                ],
                "n_features": 8,
                "metrics_test_2024": {"recall": 0.82},
            }
        }

        # Mapping département
        state.dep_mapping.clear()
        state.dep_mapping["75"] = 75

        # Mock save_prediction pour ne pas toucher à la DB
        with patch("api.routes.save_prediction"):
            yield c


@pytest.fixture
def accident_minimal():
    """Données minimales pour une prédiction (V1 - lieu/heure)."""
    return {
        "departement": "75",
        "heure": 14,
        "mois": 6,
        "jour_semaine": 2,
        "luminosite": "jour",
    }
