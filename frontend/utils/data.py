"""Chargement et mise en cache des données partagées entre les pages."""

import json
import pandas as pd
import streamlit as st

from utils.config import DATA_DIR, MODELS_DIR


@st.cache_data
def load_metadata() -> dict:
    """Charge les métadonnées des modèles (versions, features, métriques)."""
    path = MODELS_DIR / "metadata_UC1_api.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


@st.cache_data
def load_dataset() -> pd.DataFrame:
    """Charge le dataset V4 complet (2021-2024)."""
    path = DATA_DIR / "UC1_v4_collision.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()
