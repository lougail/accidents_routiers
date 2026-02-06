"""Tests des endpoints de l'API."""


def test_health_sans_modeles(client):
    """GET /health sans modèles → status 200, status='no_models'."""
    # Appelle l'endpoint /health
    response = client.get("/health")
    # Vérifie que le status code est 200
    assert response.status_code == 200
    # Vérifie que le JSON contient status="no_models"
    assert response.json()["status"] == "no_models"


def test_predict_sans_modeles(client, accident_minimal):
    """POST /predict sans modèles → status 503."""
    # Envoie une requête POST à /predict avec accident_minimal
    response = client.post("/predict", json=accident_minimal)
    # Vérifie que le status code est 503
    assert response.status_code == 503


def test_predict_avec_modele(client_with_model, accident_minimal):
    """POST /predict avec modèle → status 200, probabilité 0.75, grave=True."""
    # Envoie une requête POST à /predict avec accident_minimal
    response = client_with_model.post("/predict", json=accident_minimal)
    # Vérifie que le status code est 200
    assert response.status_code == 200
    # Vérifie que le JSON est valide
    data = response.json()
    # Vérifie que la probabilité est 0.75
    assert data["probabilite"] == 0.75
    # Vérifie que le grave est True
    assert data["grave"] is True  # 0.75 >= 0.45
    # Vérifie que la version du modèle est v1_base
    assert data["version_modele"] == "v1_base"


def test_predict_donnees_invalides(client_with_model):
    """POST /predict avec données invalides → status 422."""
    # Envoie une requête POST à /predict avec données invalides
    response = client_with_model.post("/predict", json={"heure": 99})
    # Vérifie que le status code est 422
    assert response.status_code == 422


def test_feature_importances_sans_modeles(client):
    """GET /feature-importances sans modèles → dict vide."""
    # Appelle l'endpoint /feature-importances
    response = client.get("/feature-importances")
    # Vérifie que le status code est 200
    assert response.status_code == 200
    # Vérifie que le JSON est vide
    assert response.json() == {}
