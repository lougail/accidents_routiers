"""Page de prédiction de gravité d'un accident."""

import plotly.graph_objects as go
import requests
import streamlit as st
from utils.config import API_URL, DEPARTMENTS, VERSION_LABELS


def check_api() -> tuple[bool, dict]:
    """Vérifie la connexion à l'API et retourne (ok, health_data)."""
    try:
        r = requests.get(f"{API_URL}/health", timeout=2)
        if r.status_code == 200:
            return True, r.json()
    except requests.ConnectionError:
        pass
    return False, {}


def render_form() -> dict | None:
    """Affiche le formulaire et retourne le payload si soumis, sinon None."""
    # --- Section 1 : Quand et où (toujours requis) ---
    st.subheader("1. Quand et où ?")
    c1, c2, c3 = st.columns(3)

    with c1:
        dep_options = [f"{code} — {name}" for code, name in sorted(DEPARTMENTS.items())]
        dep_selected = st.selectbox(
            "Département", dep_options, index=dep_options.index("75 — Paris")
        )
        departement = dep_selected.split(" — ")[0]

    with c2:
        heure = st.slider("Heure", 0, 23, 14)
        mois = st.slider("Mois", 1, 12, 6)

    with c3:
        jours = [
            "Lundi",
            "Mardi",
            "Mercredi",
            "Jeudi",
            "Vendredi",
            "Samedi",
            "Dimanche",
        ]
        jour_semaine = st.selectbox("Jour", jours, index=0)
        jour_idx = jours.index(jour_semaine)

        lum_options = ["Jour", "Nuit éclairée", "Nuit non éclairée"]
        luminosite = st.selectbox("Luminosité", lum_options)
        lum_map = {
            "Jour": "jour",
            "Nuit éclairée": "nuit_eclairee",
            "Nuit non éclairée": "nuit_non_eclairee",
        }

    # --- Section 2 : Route (optionnel) ---
    with st.expander("2. Caractéristiques de la route (optionnel)"):
        use_s2 = st.checkbox("Renseigner les infos route", value=False)
        if use_s2:
            c4, c5 = st.columns(2)
            with c4:
                vma = st.slider("VMA (km/h)", 20, 130, 50)
                nbv = st.number_input("Nombre de voies", 1, 10, 2)
                type_route = st.selectbox(
                    "Type de route",
                    ["Communale", "Départementale", "Autoroute", "Autre"],
                )
            with c5:
                en_agglo = st.checkbox("En agglomération", value=True)
                bidirect = st.checkbox("Bidirectionnelle", value=False)
                meteo_deg = st.checkbox("Météo dégradée", value=False)
                surface_glis = st.checkbox("Surface glissante", value=False)
                intersect = st.checkbox("Intersection", value=False)
                pente = st.checkbox("Route en pente", value=False)

    # --- Section 3 : Véhicules (optionnel) ---
    with st.expander("3. Véhicules impliqués (optionnel)"):
        use_s3 = st.checkbox("Renseigner les véhicules", value=False)
        if use_s3:
            nb_veh = st.number_input("Nombre de véhicules", 1, 20, 2)
            types_veh = st.multiselect(
                "Types de véhicules",
                ["moto", "velo", "edp", "cyclomoteur", "pieton", "poids_lourd"],
            )

    # --- Section 4 : Collision (optionnel) ---
    with st.expander("4. Type de collision (optionnel)"):
        use_s4 = st.checkbox("Renseigner la collision", value=False)
        if use_s4:
            type_col = st.selectbox(
                "Type de collision",
                ["Frontale", "Arrière", "Côté", "Solo (sans collision)"],
            )
            col_map = {
                "Frontale": "frontale",
                "Arrière": "arriere",
                "Côté": "cote",
                "Solo (sans collision)": "solo",
            }

    # --- Soumission ---
    if not st.button("\U0001f6a8 Prédire la gravité", type="primary"):
        return None

    payload = {
        "departement": departement,
        "heure": heure,
        "mois": mois,
        "jour_semaine": jour_idx,
        "luminosite": lum_map[luminosite],
    }
    if use_s2:
        payload.update(
            {
                "vma": vma,
                "nbv": int(nbv),
                "type_route": type_route.lower(),
                "en_agglomeration": en_agglo,
                "bidirectionnelle": bidirect,
                "meteo_degradee": meteo_deg,
                "surface_glissante": surface_glis,
                "intersection": intersect,
                "route_en_pente": pente,
            }
        )
    if use_s3:
        payload["nb_vehicules"] = int(nb_veh)
        if types_veh:
            payload["types_vehicules"] = types_veh
    if use_s4:
        payload["type_collision"] = col_map[type_col]

    return payload


def render_result(pred: dict):
    """Affiche la jauge de probabilité et le verdict."""
    proba = pred["probabilite"]
    grave = pred["grave"]
    color = "red" if grave else "green"

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=proba * 100,
            number={"suffix": "%"},
            title={"text": "Probabilité de gravité"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": color},
                "steps": [
                    {"range": [0, 45], "color": "#d4edda"},
                    {"range": [45, 100], "color": "#f8d7da"},
                ],
                "threshold": {
                    "line": {"color": "black", "width": 3},
                    "thickness": 0.8,
                    "value": pred["seuil"] * 100,
                },
            },
        )
    )
    fig.update_layout(height=300, margin=dict(t=60, b=0))
    st.plotly_chart(fig, use_container_width=True)

    if grave:
        st.error(f"ALERTE — Accident probablement GRAVE ({proba:.0%})")
        st.markdown("Envoi de moyens renforcés recommandé (SMUR, hélicoptère)")
    else:
        st.success(f"Accident probablement non grave ({proba:.0%})")
        st.markdown("Intervention standard recommandée")

    with st.expander("Détails techniques"):
        version = pred["version_modele"]
        st.write(f"**Modèle** : {VERSION_LABELS.get(version, version)}")
        st.write(f"**Features utilisées** : {pred['n_features']}")
        st.write(f"**Seuil** : {pred['seuil']}")
        m = pred.get("metriques_modele", {})
        if m:
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("ROC-AUC", f"{m.get('roc_auc', 0):.3f}")
            mc2.metric("Recall", f"{m.get('recall_at_threshold', 0):.3f}")
            mc3.metric("Precision", f"{m.get('precision_at_threshold', 0):.3f}")


# --- Point d'entrée de la page ---

st.title("Prédiction de gravité d'un accident")
st.caption(
    "Remplissez les informations disponibles. "
    "Le modèle s'adapte automatiquement au niveau de détail fourni."
)

api_ok, health = check_api()
if api_ok:
    st.sidebar.success(f"API connectée — {health['n_models']} modèle(s)")
else:
    st.sidebar.error("API non disponible. Lancez : `uvicorn api.main:app`")

col_form, col_result = st.columns([2, 1])

with col_form:
    payload = render_form()

    if payload and api_ok:
        try:
            r = requests.post(f"{API_URL}/predict", json=payload, timeout=10)
            if r.status_code == 200:
                st.session_state["prediction"] = r.json()
            else:
                st.error(f"Erreur API : {r.text}")
        except Exception as e:
            st.error(f"Erreur : {e}")

with col_result:
    st.subheader("Résultat")
    if "prediction" in st.session_state:
        render_result(st.session_state["prediction"])
    else:
        st.info("Remplissez le formulaire et cliquez sur Prédire")
