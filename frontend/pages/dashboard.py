"""Page dashboard — visualisations et statistiques des accidents."""

import json
from urllib.request import urlopen

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
from plotly.subplots import make_subplots
from utils.config import API_URL, DEPARTMENTS, VERSION_LABELS, feature_label
from utils.data import load_dataset, load_metadata

GEOJSON_URL = (
    "https://raw.githubusercontent.com/gregoiredavid/france-geojson/"
    "master/departements-version-simplifiee.geojson"
)


@st.cache_data
def load_geojson() -> dict:
    """Charge le GeoJSON des départements français (mis en cache)."""
    with urlopen(GEOJSON_URL) as response:
        return json.load(response)


# --- Sections du dashboard ---


def section_kpis(df: pd.DataFrame, meta: dict):
    """KPIs principaux en haut de page."""
    best_metrics = (
        meta.get("models", {})
        .get("v4_collision", {})
        .get("metrics_test_2024", {})
    )

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total accidents", f"{len(df):,}")
    k2.metric("Accidents graves", f"{int(df['grave'].sum()):,}")
    k3.metric("Taux de gravité", f"{df['grave'].mean():.1%}")
    k4.metric("ROC-AUC (V4)", f"{best_metrics.get('roc_auc', 0):.3f}")


def section_impact_operationnel(df: pd.DataFrame, meta: dict):
    """Traduction du recall en chiffres concrets pour les secours."""
    st.subheader("Impact opérationnel du modèle")

    best_recall = (
        meta.get("models", {})
        .get("v4_collision", {})
        .get("metrics_test_2024", {})
        .get("recall_at_threshold", 0)
    )

    nb_graves_2024 = int(df[df["annee"] == 2024]["grave"].sum()) if "annee" in df.columns else 0
    nb_detectes = int(nb_graves_2024 * best_recall)
    nb_manques = nb_graves_2024 - nb_detectes

    io1, io2, io3 = st.columns(3)
    io1.metric("Accidents graves en 2024", f"{nb_graves_2024:,}")
    io2.metric(
        "Détectés par le modèle (recall)",
        f"{nb_detectes:,}",
        delta=f"{best_recall:.0%} détectés",
        delta_color="normal",
    )
    io3.metric(
        "Non détectés",
        f"{nb_manques:,}",
        delta=f"{1 - best_recall:.0%} manqués",
        delta_color="inverse",
    )
    st.caption(
        f"Le modèle V4 identifie correctement {best_recall:.0%} des accidents graves. "
        "Cela permet d'envoyer des moyens renforcés (SMUR, héliportage) "
        "dès l'appel initial, avant même l'arrivée des premiers secours."
    )


def section_distributions_temporelles(df: pd.DataFrame):
    """Accidents par heure et par mois, couleur = taux de gravité."""
    st.subheader("Distributions temporelles")
    t1, t2 = st.columns(2)

    with t1:
        hourly = df.groupby("heure")["grave"].agg(["mean", "count"]).reset_index()
        hourly.columns = ["heure", "taux_gravite", "nb_accidents"]
        fig = px.bar(
            hourly, x="heure", y="nb_accidents",
            color="taux_gravite", color_continuous_scale="RdYlGn_r",
            title="Accidents par heure (couleur = taux de gravité)",
            labels={"nb_accidents": "Nombre", "taux_gravite": "Taux gravité"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with t2:
        monthly = df.groupby("mois")["grave"].agg(["mean", "count"]).reset_index()
        monthly.columns = ["mois", "taux_gravite", "nb_accidents"]
        mois_noms = {
            1: "Jan", 2: "Fév", 3: "Mar", 4: "Avr", 5: "Mai", 6: "Juin",
            7: "Jul", 8: "Aoû", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Déc",
        }
        monthly["mois_nom"] = monthly["mois"].map(mois_noms)
        fig = px.bar(
            monthly, x="mois_nom", y="nb_accidents",
            color="taux_gravite", color_continuous_scale="RdYlGn_r",
            title="Accidents par mois",
            labels={"nb_accidents": "Nombre", "taux_gravite": "Taux gravité", "mois_nom": "Mois"},
        )
        st.plotly_chart(fig, use_container_width=True)


def section_geographie(df: pd.DataFrame):
    """Carte choropleth + top 15 départements."""
    st.subheader("Répartition géographique")

    dep_stats = (
        df.groupby("dep")["grave"]
        .agg(["count", "sum", "mean"])
        .reset_index()
    )
    dep_stats.columns = ["dep", "nb_accidents", "nb_graves", "taux_gravite"]
    dep_stats["nom"] = dep_stats["dep"].map(DEPARTMENTS)
    dep_stats["label"] = dep_stats["dep"] + " — " + dep_stats["nom"].fillna("")

    # --- Carte choropleth ---
    geojson = load_geojson()

    metric_choice = st.radio(
        "Métrique affichée sur la carte",
        ["Taux de gravité", "Nombre d'accidents"],
        horizontal=True,
    )
    color_col = "taux_gravite" if metric_choice == "Taux de gravité" else "nb_accidents"
    color_scale = "Reds" if color_col == "taux_gravite" else "Blues"

    fig_map = px.choropleth(
        dep_stats,
        geojson=geojson,
        locations="dep",
        featureidkey="properties.code",
        color=color_col,
        hover_name="nom",
        hover_data={"dep": True, "nb_accidents": True, "taux_gravite": ":.1%"},
        color_continuous_scale=color_scale,
        title=f"{metric_choice} par département",
        labels={"taux_gravite": "Taux gravité", "nb_accidents": "Nb accidents", "dep": "Code"},
    )
    fig_map.update_geos(fitbounds="locations", visible=False)
    fig_map.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0}, height=500)
    st.plotly_chart(fig_map, use_container_width=True)

    # --- Top 15 barres ---
    g1, g2 = st.columns(2)

    with g1:
        top_volume = dep_stats.nlargest(15, "nb_accidents").sort_values("nb_accidents")
        fig = px.bar(
            top_volume, x="nb_accidents", y="label", orientation="h",
            color="taux_gravite", color_continuous_scale="RdYlGn_r",
            title="Top 15 départements (volume)",
            labels={"nb_accidents": "Nombre d'accidents", "label": "", "taux_gravite": "Taux gravité"},
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

    with g2:
        dep_enough = dep_stats[dep_stats["nb_accidents"] >= 500]
        top_gravite = dep_enough.nlargest(15, "taux_gravite").sort_values("taux_gravite")
        fig = px.bar(
            top_gravite, x="taux_gravite", y="label", orientation="h",
            color="taux_gravite", color_continuous_scale="Reds",
            title="Top 15 départements (taux de gravité)",
            labels={"taux_gravite": "Taux de gravité", "label": ""},
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)


def section_facteurs_risque(df: pd.DataFrame):
    """Ratio de gravité pour les facteurs binaires clés."""
    st.subheader("Facteurs de risque")

    risk_features = [
        "hors_agglo", "bidirectionnelle", "haute_vitesse", "meteo_degradee",
        "surface_glissante", "has_moto", "has_velo", "has_pieton",
        "has_vehicule_lourd", "collision_frontale", "collision_solo",
        "nuit", "weekend", "intersection_complexe",
    ]
    available = [f for f in risk_features if f in df.columns]

    risk_data = []
    for feat in available:
        taux_present = df[df[feat] == 1]["grave"].mean()
        taux_absent = df[df[feat] == 0]["grave"].mean()
        risk_data.append({
            "feature": feature_label(feat),
            "ratio": taux_present / taux_absent if taux_absent > 0 else 0,
        })

    df_risk = pd.DataFrame(risk_data).sort_values("ratio", ascending=True)
    fig = px.bar(
        df_risk, x="ratio", y="feature", orientation="h",
        color="ratio", color_continuous_scale="Reds",
        title="Ratio de gravité (présent vs absent)",
        labels={"ratio": "Ratio de risque", "feature": ""},
    )
    fig.add_vline(x=1, line_dash="dash", line_color="gray", annotation_text="Référence (x1)")
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Un ratio > 1 signifie que la présence de ce facteur augmente le taux de gravité. "
        "Par exemple, un ratio de 2 signifie que le taux de gravité est 2x plus élevé."
    )


def section_feature_importance():
    """Feature importance des modèles via l'API."""
    st.subheader("Feature importance du modèle")
    try:
        r = requests.get(f"{API_URL}/feature-importances", timeout=5)
        if r.status_code != 200:
            return
    except requests.ConnectionError:
        st.warning("API non disponible — feature importance indisponible.")
        return

    fi_data = r.json()
    version_sel = st.selectbox("Version du modèle", list(fi_data.keys()))

    if version_sel not in fi_data:
        return

    fi_df = pd.DataFrame(fi_data[version_sel])
    fi_df["label"] = fi_df["feature"].map(feature_label)
    fig = px.bar(
        fi_df.sort_values("importance"), x="importance", y="label", orientation="h",
        color="importance", color_continuous_scale="Blues",
        title=f"Top 15 features — {version_sel}",
        labels={"label": "", "importance": "Importance"},
    )
    fig.update_layout(height=500, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def section_comparaison_modeles(meta: dict):
    """Comparaison des métriques V1 à V4."""
    st.subheader("Performance par niveau d'information")

    if not meta or "models" not in meta:
        return

    perf_data = []
    for version, info in meta["models"].items():
        m = info.get("metrics_test_2024", {})
        perf_data.append({
            "version": VERSION_LABELS.get(version, version),
            "ROC-AUC": m.get("roc_auc", 0),
            "Recall": m.get("recall_at_threshold", 0),
            "Precision": m.get("precision_at_threshold", 0),
        })

    df_perf = pd.DataFrame(perf_data)
    colors = {"ROC-AUC": "#636EFA", "Recall": "#EF553B", "Precision": "#00CC96"}

    fig = go.Figure()
    for metric in ("ROC-AUC", "Recall", "Precision"):
        fig.add_trace(go.Bar(
            name=metric,
            x=df_perf["version"],
            y=df_perf[metric],
            marker_color=colors[metric],
            text=df_perf[metric].apply(lambda v: f"{v:.2f}"),
            textposition="outside",
        ))
    fig.update_layout(barmode="group", title="Métriques par version (test 2024)", yaxis_range=[0, 1], height=400)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Chaque version correspond au niveau d'information disponible lors de l'appel. "
        "V1 = seuls le lieu et l'heure sont connus. V4 = toutes les informations. "
        "L'API sélectionne automatiquement le modèle adapté."
    )


def section_evolution_annuelle(df: pd.DataFrame):
    """Volume d'accidents et taux de gravité par année."""
    if "annee" not in df.columns:
        return

    st.subheader("Évolution annuelle")

    yearly = (
        df.groupby("annee")
        .agg(nb_accidents=("grave", "count"), nb_graves=("grave", "sum"), taux=("grave", "mean"))
        .reset_index()
    )
    yearly["annee_str"] = yearly["annee"].astype(str)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(
            x=yearly["annee_str"], y=yearly["nb_accidents"],
            name="Total accidents", marker_color="steelblue",
            text=yearly["nb_accidents"].apply(lambda v: f"{v:,}"),
            textposition="outside",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=yearly["annee_str"], y=yearly["taux"] * 100,
            name="Taux gravité (%)", mode="lines+markers+text",
            text=yearly["taux"].apply(lambda v: f"{v:.1%}"),
            textposition="top center",
            line=dict(color="crimson", width=3),
            marker=dict(size=10),
        ),
        secondary_y=True,
    )
    fig.update_layout(title="Accidents par année", height=400)
    fig.update_xaxes(type="category")
    fig.update_yaxes(title_text="Nombre d'accidents", secondary_y=False)
    fig.update_yaxes(title_text="Taux de gravité (%)", secondary_y=True, range=[0, 50])
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Le taux de gravité est stable autour de 35% sur les 4 années. "
        "Le volume d'accidents est également constant (~52 000/an)."
    )


# --- Point d'entrée de la page ---

st.title("Dashboard — Accidents routiers 2021-2024")

df = load_dataset()
if df.empty:
    st.error("Dataset introuvable. Exécutez d'abord le notebook 04a.")
    st.stop()

meta = load_metadata()

section_kpis(df, meta)
st.divider()
section_impact_operationnel(df, meta)
st.divider()
section_distributions_temporelles(df)
section_geographie(df)
section_facteurs_risque(df)
section_feature_importance()
section_comparaison_modeles(meta)
section_evolution_annuelle(df)
