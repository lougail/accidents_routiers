"""
UC1 — API de Priorisation des Secours
Prédiction de la gravité des accidents routiers

Lancement :
  uvicorn api.main:app --reload
"""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from api import state
from api.database import init_db
from api.metrics import models_loaded
from api.model import load_all_models
from api.routes import router

# Origines autorisées pour CORS (configurable via env)
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS", "http://localhost:8501,http://frontend:8501"
).split(",")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Charge les modèles au démarrage, libère les ressources à l'arrêt."""
    state.models, state.metadata, state.dep_mapping = load_all_models()
    models_loaded.set(len(state.models))
    init_db()
    yield
    state.models.clear()
    state.metadata.clear()
    state.dep_mapping.clear()


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

app.include_router(router)

Instrumentator().instrument(app).expose(app)
