# Exercices PromQL

## 1. Taux de requetes HTTP par seconde (toutes routes)

```promql
sum(rate(http_requests_total[5m]))
```

Calcule le nombre moyen de requetes par seconde sur les 5 dernieres minutes. `rate()` transforme un compteur cumule en taux instantane, `sum()` agregue toutes les routes.

## 2. Taux d'erreur 5xx en pourcentage

```promql
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100
```

Filtre les requetes avec un status code 5xx via le regex `5..`, divise par le total, multiplie par 100. Resultat en pourcentage.

## 3. Latence P95 des requetes HTTP

```promql
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
```

`histogram_quantile` calcule le 95e percentile a partir des buckets d'un histogramme. Le `by (le)` est obligatoire pour grouper par borne superieure de bucket.

## 4. Nombre de predictions par version de modele

```promql
sum(rate(predictions_total[5m])) by (version)
```

Utilise le label `version` (v1_base, v2_route, etc.) pour ventiler le debit de predictions par modele. Permet de voir quel modele est le plus sollicite.

## 5. Utilisation CPU du host

```promql
100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

Node Exporter expose le temps CPU par mode. On prend le mode `idle`, on calcule son taux, et on le soustrait de 100% pour obtenir l'utilisation reelle.

## 6. Memoire RAM utilisee en pourcentage

```promql
(1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100
```

Ratio entre la memoire disponible et la memoire totale, inverse et multiplie par 100. `MemAvailable` est plus fiable que `MemFree` car il inclut les buffers/cache recuperables.
