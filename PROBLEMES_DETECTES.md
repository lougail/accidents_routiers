# Problèmes détectés

Analyse du projet avec ruff, mypy, bandit et revue manuelle.

---

## 🔒 Sécurité (2 problèmes)

~~1. **Credentials en clair dans le repo**~~ ✅ Faux problème — les fichiers `.env` sont dans `.gitignore`, seuls les `.example` avec `changeme` sont trackés.

~~2. **Pas de validation stricte sur `luminosite`**~~ ✅ Corrigé avec `Literal["jour", "nuit_eclairee", "nuit_non_eclairee"]`

~~3. **Pas de validation stricte sur `type_route`**~~ ✅ Corrigé avec `Literal["autoroute", "departementale", "communale", "autre"]`

4. **Pas de rate limiting** — L'API est vulnérable au spam. N'importe qui peut envoyer des milliers de requêtes.

---

## 🏷️ Typage — API (8 problèmes)

~~5. **`database.py:14`** — mypy error: `Base` n'est pas valide comme type.~~ ✅ Corrigé avec migration SQLAlchemy 2.0

6. **`main.py:31-33`** — `models: dict = {}` pas typé précisément. Devrait être `dict[str, CatBoostClassifier]`.

~~7. **`main.py:68`** — `def health()` pas de type de retour explicite.~~ ✅ Corrigé `-> HealthResponse`

~~8. **`main.py:79`** — `def predict(data: AccidentInput)` pas de type de retour explicite.~~ ✅ Corrigé `-> PredictionResponse`

~~9. **`main.py:122`** — `def feature_importances()` pas de type de retour explicite.~~ ✅ Corrigé `-> dict[str, list[dict[str, float]]]`

10. **`model.py:47`** — `def detect_version(data)` — paramètre `data` pas typé. Devrait être `data: AccidentInput`.

11. **`model.py:58`** — `def build_features(data, ...)` — paramètre `data` pas typé.

~~12. **`database.py:30`** — `def save_prediction(...)` — pas de type de retour.~~ ✅ Corrigé avec SQLAlchemy 2.0

---

## 🏷️ Typage — Frontend (10 problèmes)

13. **`frontend/app.py:20-22`** — `st.navigation` et `st.Page` non reconnus par mypy (nouvelle API Streamlit 1.36+).

14. **`frontend/pages/prediction.py:4`** — Library stubs manquants pour `requests`. Fix: `uv add --group dev types-requests`.

15. **`frontend/pages/prediction.py:30`** — Variable peut être `None` mais `.split()` appelé sans vérification.

16. **`frontend/pages/prediction.py:39`** — Argument potentiellement `None` passé à `list.index()`.

17. **`frontend/pages/prediction.py:93`** — Index `str | None` utilisé sur un `dict[str, str]`.

18. **`frontend/pages/prediction.py:99`** — `.lower()` appelé sur une variable potentiellement `None`.

19. **`frontend/pages/prediction.py:112`** — Index `str | None` utilisé sur un `dict[str, str]`.

20. **`frontend/pages/dashboard.py:7`** — Library stubs manquants pour `requests`.

21. **`frontend/pages/dashboard.py:346`** — `st.divider()` non reconnu par mypy.

22. **`frontend/pages/dashboard.py:348`** — `st.divider()` non reconnu par mypy.

---

## ♻️ Anti-patterns (5 problèmes)

23. **`main.py:39`** — Utilisation de `global` pour `models`, `metadata`, `dep_mapping`. Anti-pattern. Préférer une classe `AppState` ou `app.state`.

24. **`database.py:31-42`** — Pas de gestion d'erreur si la base de données est inaccessible. Un crash DB fait planter l'API silencieusement.

~~25. **`model.py:25-26`** — Utilisation de `print()` au lieu d'un logger.~~ ✅ Corrigé avec `logging.error()`

~~26. **`model.py:39-41`** — Idem, `print()` pour les logs.~~ ✅ Corrigé avec `logging.info()` et `logging.warning()`

27. **`model.py:60`** — Variable nommée `f` peu explicite. Devrait être `features` ou `feature_dict`.

---

## 📝 Documentation (5 problèmes)

28. **`database.py`** — Pas de docstring au niveau du module.

29. **`database.py:14`** — Classe `Prediction` sans docstring.

30. **`database.py:26`** — Fonction `init_db()` sans docstring.

31. **`database.py:30`** — Fonction `save_prediction()` sans docstring.

32. **`main.py:122`** — `feature_importances()` a une docstring minimale (une ligne). Manque la description des retours.

---

## 🎨 Style — CORRIGÉS

~~33. Imports mal triés dans `api/database.py`~~ ✅ Fixé par `ruff --fix`

~~34. Imports mal triés dans `api/main.py`~~ ✅ Fixé par `ruff --fix`

~~35. Imports mal triés dans `api/model.py`~~ ✅ Fixé par `ruff --fix`

~~36. Imports mal triés dans `frontend/`~~ ✅ Fixé par `ruff --fix`

~~37. Pas de newline à la fin de `database.py`~~ ✅ Fixé par `ruff --fix`

---

## 📋 Résumé

| Catégorie | Total | Corrigés | Restants |
|-----------|-------|----------|----------|
| Sécurité | 4 | 3 ✅ | 1 |
| Typage API | 8 | 5 ✅ | 3 |
| Typage Frontend | 10 | 0 | 10 |
| Anti-patterns | 5 | 2 ✅ | 3 |
| Documentation | 5 | 0 | 5 |
| Style | 5 | 5 ✅ | 0 |
| **Total** | **37** | **15 ✅** | **22** |

---

## Corrections effectuées

1. ✅ `print()` → `logging` dans `model.py`
2. ✅ Validation `Literal` sur `luminosite`, `type_route`, `type_collision`, `types_vehicules` dans `schemas.py`
3. ✅ Types de retour sur `health()`, `predict()`, `feature_importances()` dans `main.py`
4. ✅ Migration SQLAlchemy 2.0 dans `database.py` (résout erreurs mypy)
5. ✅ Imports triés avec `ruff --fix`

---

## Outils utilisés

```bash
uv run ruff check .          # 0 erreur ✅
uv run mypy api/             # 0 erreur ✅
uv run bandit -r api/        # 0 issue ✅
```

---

## Prochaines étapes (optionnel)

1. Ajouter rate limiting (ex: `slowapi`)
2. Typer les paramètres `data` dans `model.py`
3. Ajouter `types-requests` aux dépendances dev
4. Ajouter les docstrings manquantes
5. Refactorer le `global` en `app.state`
