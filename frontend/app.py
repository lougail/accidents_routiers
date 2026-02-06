"""
UC1 — Interface de Priorisation des Secours

Application Streamlit multipage pour la prédiction de gravité
des accidents routiers et la visualisation des données BAAC 2021-2024.

Lancement :
    streamlit run frontend/app.py
"""

import streamlit as st

st.set_page_config(
    page_title="UC1 — Priorisation des Secours",
    page_icon="\U0001f691",
    layout="wide",
)

# --- Navigation ---
pg = st.navigation(
    [
        st.Page(
            "pages/prediction.py", title="Prédiction", icon="\U0001f3af", default=True
        ),
        st.Page("pages/dashboard.py", title="Dashboard", icon="\U0001f4ca"),
    ]
)

pg.run()
