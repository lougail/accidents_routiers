"""Genere des predictions variees pour alimenter les dashboards Grafana."""

import random
import time

import requests

API_URL = "http://localhost:8000/predict"

# Donnees de base pour les predictions
DEPARTEMENTS = ["75", "13", "69", "31", "33", "44", "59", "67", "2A", "974"]
LUMINOSITES = ["jour", "nuit_eclairee", "nuit_non_eclairee"]
TYPES_ROUTE = ["autoroute", "departementale", "communale", "autre"]
TYPES_VEHICULES = ["moto", "velo", "edp", "cyclomoteur", "pieton", "poids_lourd"]
TYPES_COLLISION = ["frontale", "arriere", "cote", "solo"]


def make_v1():
    """Prediction V1 : lieu + heure."""
    return {
        "departement": random.choice(DEPARTEMENTS),
        "heure": random.randint(0, 23),
        "mois": random.randint(1, 12),
        "jour_semaine": random.randint(0, 6),
        "luminosite": random.choice(LUMINOSITES),
    }


def make_v2():
    """Prediction V2 : + route."""
    data = make_v1()
    data.update(
        {
            "vma": random.choice([30, 50, 70, 90, 110, 130]),
            "nbv": random.randint(1, 4),
            "type_route": random.choice(TYPES_ROUTE),
            "en_agglomeration": random.choice([True, False]),
            "bidirectionnelle": random.choice([True, False]),
            "meteo_degradee": random.choice([True, False]),
            "surface_glissante": random.choice([True, False]),
            "intersection": random.choice([True, False]),
            "route_en_pente": random.choice([True, False]),
        }
    )
    return data


def make_v3():
    """Prediction V3 : + vehicules."""
    data = make_v2()
    nb = random.randint(1, 4)
    data.update(
        {
            "nb_vehicules": nb,
            "types_vehicules": random.sample(
                TYPES_VEHICULES, k=min(nb, len(TYPES_VEHICULES))
            ),
        }
    )
    return data


def make_v4():
    """Prediction V4 : + collision."""
    data = make_v3()
    data["type_collision"] = random.choice(TYPES_COLLISION)
    return data


VERSIONS = [make_v1, make_v2, make_v3, make_v4]

if __name__ == "__main__":
    n = 50
    ok = 0
    errors = 0

    for i in range(n):
        data = random.choice(VERSIONS)()
        try:
            r = requests.post(API_URL, json=data, timeout=10)
            if r.status_code == 200:
                result = r.json()
                grave = "GRAVE" if result["grave"] else "non grave"
                print(
                    f"[{i + 1}/{n}] {result['version_modele']} "
                    f"→ {grave} ({result['probabilite']:.0%})"
                )
                ok += 1
            else:
                print(f"[{i + 1}/{n}] Erreur {r.status_code}: {r.text[:80]}")
                errors += 1
        except requests.exceptions.ConnectionError:
            print(f"[{i + 1}/{n}] API inaccessible")
            errors += 1

        time.sleep(0.2)

    print(f"\nTermine : {ok} OK, {errors} erreurs")
