"""Fixtures partagées pour les tests."""

from unittest.mock import Mock, patch

import numpy as np
import pytest
from fastapi.testclient import TestClient

import api.main


@pytest.fixture
def client():
    """Client de test FastAPI sans modèles chargés.

    Le lifespan charge les modèles au démarrage.
    On les vide ensuite pour tester le comportement sans modèles.
    """
    with TestClient(api.main.app, raise_server_exceptions=False) as c:
        api.main.models.clear()
        api.main.metadata.clear()
        api.main.dep_mapping.clear()
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
        api.main.models.clear()
        api.main.models["v1_base"] = fake_model

        # Métadonnées minimales (liste de features attendues par build_features)
        api.main.metadata.clear()
        api.main.metadata["threshold"] = 0.45
        api.main.metadata["models"] = {
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
        api.main.dep_mapping.clear()
        api.main.dep_mapping["75"] = 75

        # Mock save_prediction pour ne pas toucher à la DB
        with patch("api.main.save_prediction"):
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
