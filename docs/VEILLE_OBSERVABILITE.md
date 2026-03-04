# Veille Observabilité & Monitoring

## 1. Monitoring vs Observabilité

- **Monitoring** : surveillance de métriques prédéfinies pour détecter des problèmes connus. Approche réactive ("est-ce que ça marche ?"). Exemple : alerter quand le CPU dépasse 90%.
- **Observabilité** : capacité à comprendre l'état interne d'un système à partir des données qu'il produit. Approche exploratoire ("pourquoi ça ne marche pas ?"). Permet d'investiguer des problèmes non anticipés.

Le monitoring est un sous-ensemble de l'observabilité.

## 2. Les 3 piliers de l'observabilité

- **Métriques** : valeurs numériques mesurées dans le temps (counters, gauges, histograms). Exemple : nombre de requêtes/seconde, latence P95, taux d'erreur. Légères, idéales pour les alertes et dashboards.
- **Logs** : enregistrements textuels horodatés d'événements. Exemple : "2026-03-03 14:02:01 ERROR prediction failed for user 123". Utiles pour le debug détaillé.
- **Traces** : suivi du parcours d'une requête à travers les différents services. Exemple : requête API -> modèle ML -> base de données, avec le temps passé dans chaque étape. Essentielles en architecture microservices.

Dans ce brief, on se concentre sur le pilier **métriques** avec Prometheus et Grafana.

## 3. Architecture Prometheus (Pull vs Push)

- **Pull** : Prometheus vient chercher les métriques à intervalle régulier (ex: toutes les 15s) en appelant un endpoint `/metrics` exposé par l'application. C'est Prometheus qui initie la collecte.
- **Push** : l'application envoie elle-même ses métriques vers un serveur central à chaque événement.

Prometheus utilise le modèle **pull**. Avantages :
- Détection automatique des cibles down (si le scrape échoue)
- Pas de surcharge du collecteur si une app s'emballe
- Configuration centralisée dans Prometheus

Architecture concrète :
```
FastAPI (/metrics)  ←── Prometheus (scrape toutes les 15s) ←── Grafana (visualisation)
Node Exporter       ←──┘
cAdvisor            ←──┘
```

## 4. Les 4 types de métriques Prometheus

- **Counter** : compteur qui ne fait que monter (jamais redescendre). Repart à 0 au redémarrage. Exemple : nombre de requêtes totales, nombre d'erreurs, nombre de prédictions.
- **Gauge** : valeur instantanée qui peut monter et descendre. Exemple : nombre de connexions actives, utilisation mémoire, température.
- **Histogram** : mesure la distribution d'une valeur dans des tranches (buckets). Permet de calculer les percentiles (P50, P95, P99). Exemple : latence des requêtes (combien < 100ms, < 500ms, < 1s).
- **Summary** : similaire à Histogram mais calcule les percentiles côté application. En pratique, on préfère Histogram (plus flexible, agrégeable côté serveur).

## 5. Grafana

Outil de visualisation centralisé et multisource. Se connecte à Prometheus (et d'autres sources : PostgreSQL, Loki, etc.) pour créer des dashboards interactifs avec alertes visuelles. Prometheus a une interface basique pour tester des requêtes, mais Grafana est l'outil de référence pour le monitoring visuel en production.

## 6. PromQL (Prometheus Query Language)

Langage de requête de Prometheus pour interroger les métriques collectées.

Fonctions essentielles :
- `rate(counter[5m])` : taux par seconde d'un counter sur une fenêtre de temps
- `sum(metric)` : somme totale
- `sum(metric) by (label)` : somme groupée par label (endpoint, status, etc.)
- `histogram_quantile(0.95, rate(histogram_bucket[5m]))` : percentile 95
- `avg()`, `min()`, `max()` : agrégations classiques
- `increase(counter[1h])` : augmentation absolue sur une période

Exemples concrets :
```promql
# Prédictions par seconde
rate(predictions_total[5m])

# Taux d'erreur en %
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100

# Latence P95
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

## 7. Best Practices Prometheus

- **Nommer les métriques clairement** : `<app>_<unité>_<type>` (ex: `predictions_duration_seconds`)
- **Utiliser les bons types** : Counter pour les totaux, Gauge pour les valeurs instantanées, Histogram pour les distributions
- **Ajouter des labels pertinents** sans en abuser (chaque combinaison de labels = une série temporelle)
- **Ne pas utiliser de labels à haute cardinalité** (ex: user_id avec des millions de valeurs)
- **Incrémenter les counters après succès**, pas avant
- **Définir des buckets adaptés au domaine** pour les histograms
