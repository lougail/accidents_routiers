# Rapport de Stress Test — API Accidents Routiers UC1

## Contexte

**Objectif** : Evaluer la capacite de l'API FastAPI a tenir la charge sous differents niveaux de trafic simultane.

**Environnement** :
- Machine : macOS (OrbStack / Docker Desktop)
- API : FastAPI + 4 modeles CatBoost en memoire
- Locust et API sur la meme machine (localhost)
- Infrastructure : Docker Compose (API, PostgreSQL, Prometheus, Grafana, Node Exporter, cAdvisor)

**Limites du setup** : Locust et l'API partagent les ressources CPU/RAM de la meme machine. Le CPU observe (80-90%) inclut la charge de Locust lui-meme, ce qui signifie que Locust devient un bottleneck avant l'API. En production, avec un client distant, les resultats de latence et de throughput seraient differents.

---

## Protocole de test

- **Outil** : Locust 2.x
- **Endpoints testes** :
  - `GET /health` (poids 1)
  - `POST /predict` (poids 10) — payloads aleatoires V1 a V4
  - `GET /feature-importances` (poids 1)
- **Wait time** : 0.5 a 2 secondes entre chaque requete par utilisateur
- **Duree** : ~2-3 minutes par test
- **3 paliers** : 20, 100, 200 utilisateurs simultanes

---

## Resultats

### Test 1 — 20 utilisateurs (ramp up 5)

| Metrique | Valeur |
|----------|--------|
| RPS | 15.8 req/s |
| Failures | 0% |
| Total requetes | 22 226 |
| Median | 17 ms |
| P95 | 30 ms |
| P99 | 42 ms |
| Max | 611 ms |
| CPU | ~30% |
| RAM | ~9% |

**Analyse** : Charge legere, l'API repond sans aucune difficulte. La latence max (611ms) correspond probablement a un cold start ou une pause du garbage collector. Performance nominale excellente.

### Test 2 — 100 utilisateurs (ramp up 10)

| Metrique | Valeur |
|----------|--------|
| RPS | 79.8 req/s |
| Failures | 0% |
| Total requetes | 9 349 |
| Median | 10 ms |
| P95 | 27 ms |
| P99 | 62 ms |
| Max | 202 ms |
| CPU | ~80-90% |
| RAM | ~9.5% |

**Analyse** : Scaling lineaire parfait (x5 users → x5 RPS). La latence P95 reste stable a 27ms. Le CPU monte significativement (80-90%) mais cela inclut la charge de Locust. Aucune erreur, aucune degradation visible.

### Test 3 — 200 utilisateurs (ramp up 20)

| Metrique | Valeur |
|----------|--------|
| RPS | 158.5 req/s |
| Failures | 0% |
| Total requetes | 34 578 |
| Median | 8 ms |
| P95 | 24 ms |
| P99 | 72 ms |
| Max | 338 ms |
| CPU | ~80-90% |
| RAM | ~10.1% |

**Analyse** : Doublement du RPS par rapport au Test 2 (scaling lineaire maintenu). Zero erreur meme a 200 users simultanes. La latence P99 augmente legerement (72ms vs 62ms) mais reste tres acceptable. Le CPU plafonne autour de 80-90%, principalement du a la cohabitation Locust/API.

---

## Synthese comparative

| Metrique | 20 users | 100 users | 200 users |
|----------|----------|-----------|-----------|
| **RPS** | 15.8 | 79.8 | 158.5 |
| **Failures** | 0% | 0% | 0% |
| **Median** | 17 ms | 10 ms | 8 ms |
| **P95** | 30 ms | 27 ms | 24 ms |
| **P99** | 42 ms | 62 ms | 72 ms |
| **Max** | 611 ms | 202 ms | 338 ms |
| **CPU** | ~30% | ~80-90% | ~80-90% |
| **RAM** | ~9% | ~9.5% | ~10.1% |

### Observations cles

1. **Scaling lineaire** : Le throughput (RPS) scale proportionnellement au nombre d'utilisateurs, signe d'une architecture efficace sans contention majeure.

2. **Zero erreur** : Aucune requete en echec sur les 3 tests (~66 000 requetes au total). L'API est robuste et stable.

3. **Latence stable** : La P95 reste sous 30ms dans tous les scenarios. Seule la P99 montre une legere augmentation (+71% entre 20 et 200 users) qui reste negligeable en valeur absolue (72ms).

4. **RAM constante** : Les modeles CatBoost sont charges une seule fois au demarrage. L'inference n'alloue pas de memoire significative par requete.

5. **Point de rupture non atteint** : La co-localisation Locust/API sur la meme machine empeche de determiner le veritable point de rupture. Locust sature le CPU avant l'API.

---

## Preconisations d'optimisation

### 1. Ajouter des workers Uvicorn

Actuellement, l'API tourne avec un seul worker Uvicorn. En production, utiliser Gunicorn avec plusieurs workers permettrait d'exploiter tous les coeurs CPU :

```bash
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**Impact attendu** : multiplication du throughput par le nombre de workers (quasi-lineaire pour des workloads CPU-bound comme l'inference CatBoost).

### 2. Separer Locust de l'API pour un test realiste

Pour trouver le vrai point de rupture, executer Locust depuis une machine distante (ou au minimum un container Docker separe avec des limites CPU dediees). Cela eliminera le biais de partage de ressources et donnera des metriques de latence reseau realistes.

```bash
# Depuis une machine distante
locust -f locustfile.py --host http://<api-server-ip>:8000
```

### 3. Mettre en cache les feature importances

L'endpoint `/feature-importances` recalcule les importances a chaque appel alors que les modeles ne changent pas. Un cache en memoire (TTL de quelques minutes) reduirait la charge inutile :

```python
from functools import lru_cache

@lru_cache(maxsize=1)
def get_cached_importances():
    # calcul des importances...
    pass
```

**Impact attendu** : reduction de la latence de cet endpoint et liberation de CPU pour les predictions.
