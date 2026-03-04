from prometheus_client import Counter, Gauge, Histogram

predictions_total = Counter("predictions_total", "Total de prédictions", ["version"])
predictions_graves_total = Counter(
    "predictions_graves_total", "Total de prédictions graves", ["version"]
)
http_errors_total = Counter("http_errors_total", "Total d'erreurs HTTP", ["type"])

models_loaded = Gauge("models_loaded", "Nombre de modèles chargés")

prediction_duration_seconds = Histogram(
    "prediction_duration_seconds", "Durée de prédiction", ["version"]
)
