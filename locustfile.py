import random

from locust import HttpUser, between, task

DEPARTEMENTS = ["75", "13", "69", "31", "33", "44", "59", "67", "2A", "974"]
LUMINOSITES = ["jour", "nuit_eclairee", "nuit_non_eclairee"]
TYPES_ROUTE = ["autoroute", "departementale", "communale", "autre"]
TYPES_VEHICULES = ["moto", "velo", "edp", "cyclomoteur", "pieton", "poids_lourd"]
TYPES_COLLISION = ["frontale", "arriere", "cote", "solo"]


def make_v1():
    return {
        "departement": random.choice(DEPARTEMENTS),
        "heure": random.randint(0, 23),
        "mois": random.randint(1, 12),
        "jour_semaine": random.randint(0, 6),
        "luminosite": random.choice(LUMINOSITES),
    }


def make_v2():
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
    data = make_v3()
    data["type_collision"] = random.choice(TYPES_COLLISION)
    return data


VERSIONS = [make_v1, make_v2, make_v3, make_v4]


class APIUser(HttpUser):
    wait_time = between(0.5, 2)

    @task(1)
    def check_health(self):
        self.client.get("/health")

    @task(10)
    def predict(self):
        data = random.choice(VERSIONS)()
        self.client.post("/predict", json=data)

    @task(1)
    def feature_importances(self):
        self.client.get("/feature-importances")
