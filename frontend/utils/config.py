"""Constantes et configuration partagées entre les pages."""

from pathlib import Path
import os

# --- Chemins ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# Docker utilise "data/", local utilise "données/"
DATA_DIR = BASE_DIR / "data" if (BASE_DIR / "data").exists() else BASE_DIR / "données"
MODELS_DIR = BASE_DIR / "models"

# --- API ---
API_URL = os.getenv("API_URL", "http://localhost:8000")

# --- Départements ---
DEPARTMENTS = {
    "01": "Ain", "02": "Aisne", "03": "Allier", "04": "Alpes-de-Haute-Provence",
    "05": "Hautes-Alpes", "06": "Alpes-Maritimes", "07": "Ardèche", "08": "Ardennes",
    "09": "Ariège", "10": "Aube", "11": "Aude", "12": "Aveyron",
    "13": "Bouches-du-Rhône", "14": "Calvados", "15": "Cantal", "16": "Charente",
    "17": "Charente-Maritime", "18": "Cher", "19": "Corrèze", "21": "Côte-d'Or",
    "22": "Côtes-d'Armor", "23": "Creuse", "24": "Dordogne", "25": "Doubs",
    "26": "Drôme", "27": "Eure", "28": "Eure-et-Loir", "29": "Finistère",
    "2A": "Corse-du-Sud", "2B": "Haute-Corse",
    "30": "Gard", "31": "Haute-Garonne", "32": "Gers", "33": "Gironde",
    "34": "Hérault", "35": "Ille-et-Vilaine", "36": "Indre", "37": "Indre-et-Loire",
    "38": "Isère", "39": "Jura", "40": "Landes", "41": "Loir-et-Cher",
    "42": "Loire", "43": "Haute-Loire", "44": "Loire-Atlantique", "45": "Loiret",
    "46": "Lot", "47": "Lot-et-Garonne", "48": "Lozère", "49": "Maine-et-Loire",
    "50": "Manche", "51": "Marne", "52": "Haute-Marne", "53": "Mayenne",
    "54": "Meurthe-et-Moselle", "55": "Meuse", "56": "Morbihan", "57": "Moselle",
    "58": "Nièvre", "59": "Nord", "60": "Oise", "61": "Orne",
    "62": "Pas-de-Calais", "63": "Puy-de-Dôme", "64": "Pyrénées-Atlantiques",
    "65": "Hautes-Pyrénées", "66": "Pyrénées-Orientales", "67": "Bas-Rhin",
    "68": "Haut-Rhin", "69": "Rhône", "70": "Haute-Saône", "71": "Saône-et-Loire",
    "72": "Sarthe", "73": "Savoie", "74": "Haute-Savoie", "75": "Paris",
    "76": "Seine-Maritime", "77": "Seine-et-Marne", "78": "Yvelines",
    "79": "Deux-Sèvres", "80": "Somme", "81": "Tarn", "82": "Tarn-et-Garonne",
    "83": "Var", "84": "Vaucluse", "85": "Vendée", "86": "Vienne",
    "87": "Haute-Vienne", "88": "Vosges", "89": "Yonne",
    "90": "Territoire de Belfort", "91": "Essonne", "92": "Hauts-de-Seine",
    "93": "Seine-Saint-Denis", "94": "Val-de-Marne", "95": "Val-d'Oise",
}

# --- Labels lisibles pour les features ---
FEATURE_LABELS = {
    "hors_agglo": "Hors agglomération",
    "bidirectionnelle": "Route bidirectionnelle",
    "haute_vitesse": "Vitesse >= 90 km/h",
    "meteo_degradee": "Météo dégradée",
    "surface_glissante": "Surface glissante",
    "has_moto": "Moto impliquée",
    "has_velo": "Vélo impliqué",
    "has_edp": "Trottinette (EDP)",
    "has_cyclomoteur": "Cyclomoteur impliqué",
    "has_pieton": "Piéton impliqué",
    "has_vehicule_lourd": "Poids lourd impliqué",
    "collision_frontale": "Collision frontale",
    "collision_solo": "Accident solo",
    "collision_arriere": "Collision arrière",
    "collision_cote": "Collision latérale",
    "nuit": "De nuit",
    "weekend": "Week-end",
    "intersection_complexe": "Intersection",
    "route_en_pente": "Route en pente",
    "nuit_hors_agglo": "Nuit hors agglo.",
    "collision_asymetrique": "Collision asymétrique",
    "dep": "Département",
    "heure": "Heure",
    "mois": "Mois",
    "vma": "Vitesse max. autorisée",
    "nbv": "Nombre de voies",
    "nb_vehicules": "Nombre de véhicules",
    "nuit_eclairee": "Nuit éclairée",
    "heure_pointe": "Heure de pointe",
    "heure_danger": "Heure dangereuse (2h-6h)",
    "weekend_nuit": "Week-end de nuit",
    "vitesse_x_bidirect": "Grande vitesse + bidirect.",
    "moto_x_hors_agglo": "Moto hors agglo.",
    "frontale_x_hors_agglo": "Frontale hors agglo.",
    "route_autoroute": "Autoroute",
    "route_departementale": "Départementale",
    "route_communale": "Communale",
}


def feature_label(feat: str) -> str:
    """Retourne le label lisible d'une feature, ou le nom brut si inconnu."""
    return FEATURE_LABELS.get(feat, feat)


# --- Labels des versions de modèles ---
VERSION_LABELS = {
    "v1_base": "V1 — Lieu/Heure (8 feat.)",
    "v2_route": "V2 — + Route (23 feat.)",
    "v3_vehicules": "V3 — + Véhicules (32 feat.)",
    "v4_collision": "V4 — + Collision (37 feat.)",
}
