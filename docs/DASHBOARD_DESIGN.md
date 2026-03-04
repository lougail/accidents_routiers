# Dashboard Design — Accidents Routiers UC1

## 1. HTTP Overview

**Objectif** : Vue d'ensemble de la sante de l'API (methode RED — Rate, Errors, Duration).

**Public** : SRE / DevOps / developpeur en astreinte.

### Layout

| Ligne | Panels | Type | Description |
|-------|--------|------|-------------|
| 1 — KPIs | Modeles charges | Stat | Nombre de modeles CatBoost en memoire |
| | Requetes/sec | Stat | Taux de requetes HTTP actuel |
| | Taux d'erreur | Stat (fond colore) | % d'erreurs 5xx. Vert < 1%, Jaune < 5%, Rouge > 5% |
| | Latence P95 | Stat | 95e percentile de la latence |
| 2 — Trafic | Requetes par endpoint | Time series | Debit par route (/health, /predict, /metrics) |
| | Latence P95 dans le temps | Time series | Evolution P50 + P95, seuils a 200ms et 500ms |
| 3 — Infra | CPU Usage | Time series | Utilisation CPU avec zones colorees (60/85%) |
| | Memory Usage | Gauge | % RAM utilisee (70/90%) |
| | Disk Usage | Gauge | % disque utilise (70/90%) |

### Requetes PromQL

- Requetes/sec : `sum(rate(http_requests_total[5m]))`
- Taux d'erreur : `sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100`
- Latence P95 : `histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))`
- CPU : `100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)`
- Memory : `(1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100`

---

## 2. Predictions & Performance

**Objectif** : Metriques metier du modele ML — volume de predictions, gravite, performance par version.

**Public** : Data scientist / product owner / equipe metier.

### Layout

| Ligne | Panels | Type | Description |
|-------|--------|------|-------------|
| 1 — KPIs | Total predictions | Stat | Compteur cumule de predictions |
| | Predictions graves | Stat (rouge) | Nombre de predictions classees graves |
| | Taux de gravite | Gauge | % de graves sur le total (seuils 50/75%) |
| | Duree moyenne prediction | Stat | Temps moyen d'inference par version |
| 2 — Temporel | Predictions/sec par version | Time series | Debit de predictions par modele (v1 a v4) |
| | Duree prediction par version | Time series | Latence moyenne + P95 de l'inference |
| 3 — Repartition | Predictions par version | Pie chart (donut) | Repartition des 4 versions de modele |
| | Erreurs applicatives | Time series | Erreurs metier par type (no_model, validation) |
| | RAM par container | Time series | Memoire par container Docker |

### Requetes PromQL

- Total predictions : `sum(predictions_total)`
- Predictions graves : `sum(predictions_graves_total)`
- Taux de gravite : `sum(predictions_graves_total) / sum(predictions_total) * 100`
- Predictions/sec par version : `sum(rate(predictions_total[5m])) by (version)`
- Duree moyenne : `prediction_duration_seconds_sum / prediction_duration_seconds_count`
- Repartition par version : `sum(predictions_total) by (version)`
- RAM par container : `container_memory_usage_bytes{id=~"/docker/.+"}`

---

## Choix de design

- **Pattern Z** : KPIs instantanes en haut (lecture rapide), details temporels au milieu, infrastructure en bas
- **Methode RED** appliquee : Rate (req/sec), Errors (taux erreur), Duration (latence P95)
- **Thresholds** : codes couleur vert/jaune/rouge sur tous les panels pertinents
- **Descriptions** sur chaque panel pour expliquer le "pourquoi"
- **spanNulls: true** sur les time series pour eviter les trous visuels
- **Legendes en table** avec mean/max pour les time series
- **2 dashboards complementaires** : HTTP (sante technique) et Predictions (valeur metier)
