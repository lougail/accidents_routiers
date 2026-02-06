# 📋 Comparatif des outils Python

---

## 🎨 Linters Python

**Ruff**

- Écrit en Rust par Astral (les mêmes que uv)
- Implémente les règles de Flake8, isort, pyupgrade, et d'autres dans un seul outil
- 10 à 100x plus rapide que Flake8
- Peut aussi formater le code (remplace Black)
- Configuration dans pyproject.toml
- Encore jeune : ne couvre pas 100% des règles de Pylint

**Flake8**

- Le classique, très répandu
- Combine PyFlakes (erreurs logiques) + pycodestyle (style PEP8) + McCabe (complexité)
- Écosystème de plugins riche
- Lent sur gros projets
- Configuration dans un fichier séparé (.flake8 ou setup.cfg), pas de support natif pyproject.toml

**Pylint**

- Le plus complet : détecte des erreurs que les autres ne voient pas (variables non utilisées, imports cycliques, docstrings manquants...)
- Très configurable, mais verbeux par défaut
- Très lent (peut prendre plusieurs minutes sur un gros projet)
- Beaucoup de faux positifs à configurer

| Outil | Vitesse | Règles | Facilité | Communauté | Note |
|-------|---------|--------|----------|------------|------|
| **Ruff** | Ultra-rapide | Bonne couverture (Flake8+) | Simple (pyproject.toml) | En croissance rapide | 9/10 ✅ |
| **Flake8** | Lent | Standard PEP8 | Moyenne (plugins à installer) | Mature, stable | 7/10 |
| **Pylint** | Très lent | La plus complète | Complexe (beaucoup de config) | Mature | 6/10 |

**Choix : Ruff** — Il fait le travail de Flake8 + isort + plusieurs plugins, en étant 100x plus rapide. Le seul cas où Pylint reste pertinent : si tu as besoin de règles très spécifiques qu'il est le seul à implémenter.

**À surveiller :** Pas de concurrent direct à Ruff pour l'instant. Astral domine ce segment avec Ruff qui absorbe progressivement les fonctionnalités des autres linters. La tendance est à la consolidation autour de Ruff plutôt qu'à l'émergence de nouveaux outils.

---

## 🎨 Formatters Python

**Ruff format**

- Intégré à Ruff, donc même binaire ultra-rapide
- Compatible Black à 99.9% (même style de formatage)
- Un seul outil pour linting + formatting
- Plus récent, quelques edge cases peuvent différer de Black

**Black**

- "The uncompromising code formatter" — très opinionated, peu d'options
- Devenu le standard de facto dans l'écosystème Python
- Philosophie : pas de débat sur le style, Black décide pour toi
- Seule customisation notable : longueur de ligne
- Lent comparé à Ruff format

**autopep8**

- Corrige le code pour respecter PEP8, mais de manière minimale
- Plus permissif : ne reformate que ce qui viole PEP8
- Moins "agressif" que Black (garde plus ton style original)
- Utile pour des projets legacy qu'on veut améliorer progressivement

**YAPF (Google)**

- Très configurable (contrairement à Black)
- Permet de définir son propre style
- Moins adopté, développement au ralenti

| Outil | Vitesse | Customisation | Adoption | Note |
|-------|---------|---------------|----------|------|
| **Ruff format** | Ultra-rapide | Faible (style Black) | En croissance | 9/10 ✅ |
| **Black** | Moyen | Très faible (opinionated) | Standard actuel | 8/10 |
| **autopep8** | Moyen | Moyenne | Legacy | 5/10 |
| **YAPF** | Moyen | Très haute | Faible | 5/10 |

**Choix : Ruff format** — Même résultat que Black, mais instantané. Et comme tu utilises déjà Ruff pour le linting, autant tout centraliser.

**À surveiller :** **Blue** — un fork de Black avec quelques ajustements (quotes simples par défaut, etc.). Reste marginal. La vraie tendance : Ruff format remplace progressivement Black car il est plus rapide et intégré au linter.

---

## 🔒 Type Checkers

**Mypy**

- La référence historique, créé par Guido van Rossum (créateur de Python)
- Le plus mature et le plus documenté
- Supporte les plugins pour frameworks (Django, SQLAlchemy...)
- Peut être lent sur gros projets
- Parfois strict sur des cas edge, nécessite des # type: ignore

**Pyright**

- Développé par Microsoft, écrit en TypeScript
- Utilisé par défaut dans VS Code (extension Pylance)
- Plus rapide que Mypy
- Mode strict très complet
- Excellente intégration IDE (autocomplétion, refactoring)
- Moins de plugins que Mypy

**Pyre**

- Développé par Meta (Facebook)
- Très performant sur les très gros codebases (conçu pour le monorepo de Meta)
- Inclut Pysa pour l'analyse de sécurité (taint analysis)
- Moins accessible, documentation moins fournie
- Communauté plus restreinte

| Outil | Vitesse | Précision | Intégration IDE | Communauté | Note |
|-------|---------|-----------|-----------------|------------|------|
| **Mypy** | Moyen | Très bonne | Bonne | Très large | 8/10 |
| **Pyright** | Rapide | Excellente | Excellente (VS Code) | Large | 9/10 ✅ |
| **Pyre** | Rapide | Très bonne | Moyenne | Restreinte | 6/10 |

**Choix : Pyright** — Plus rapide que Mypy, intégration parfaite avec VS Code, et mode strict très complet. Si tu utilises VS Code, Pyright est déjà là via Pylance.

Alternative : **Mypy** reste pertinent si tu as besoin de plugins spécifiques (django-stubs, sqlalchemy-stubs) ou si ton équipe le connaît déjà bien.

**À surveiller :** **Basedpyright** — un fork de Pyright avec des règles supplémentaires et moins de faux négatifs. Gagne en popularité dans la communauté qui veut un typage encore plus strict.

---

## 🧪 Frameworks de Tests

**pytest**

- Le standard de facto pour les tests Python
- Syntaxe simple : pas besoin de classes, juste des fonctions test_*
- Assertions naturelles : assert x == y au lieu de self.assertEqual(x, y)
- Système de fixtures puissant pour gérer le setup/teardown
- Écosystème de plugins énorme : pytest-cov (coverage), pytest-mock, pytest-asyncio, pytest-django...
- Excellent reporting des erreurs (affiche exactement ce qui a échoué et pourquoi)

**unittest**

- Inclus dans la standard library (pas de dépendance externe)
- Style xUnit (hérité de Java) : classes avec setUp(), tearDown(), self.assertX()
- Plus verbeux que pytest
- Suffisant pour des projets simples ou quand on veut zéro dépendance
- pytest peut exécuter des tests unittest (migration facile)

**nose2**

- Successeur de nose (abandonné)
- Entre unittest et pytest
- Peu d'avantages par rapport à pytest, communauté réduite

| Outil | Facilité | Plugins | Assertions | Communauté | Note |
|-------|----------|---------|------------|------------|------|
| **pytest** | Très simple | Énorme écosystème | Naturelles (assert) | Très large | 9/10 ✅ |
| **unittest** | Verbeux | Limités | Méthodes (self.assertX) | Standard lib | 6/10 |
| **nose2** | Moyen | Quelques-uns | Naturelles | Faible | 4/10 |

**Choix : pytest** — C'est le standard. Syntaxe simple, fixtures puissantes, plugins pour tout. Aucune raison de choisir autre chose sauf si tu veux absolument zéro dépendance (auquel cas unittest fait le job).

**À surveiller :** **ward** — un framework de test moderne avec une syntaxe encore plus expressive (descriptions en anglais naturel). Reste marginal face à pytest. **Hypothesis** n'est pas un concurrent mais un complément : il génère des tests property-based et s'intègre parfaitement avec pytest.

---

## 🔐 Security Scanners (optionnel)

**Bandit**

- Analyse statique du code Python pour détecter les failles de sécurité
- Détecte : injections SQL, utilisation de eval(), secrets hardcodés, fonctions dangereuses (pickle, subprocess avec shell=True)...
- Facile à intégrer dans la CI
- Peut générer des faux positifs qu'il faut configurer

**Safety**

- Scanne les dépendances pour trouver des vulnérabilités connues (CVE)
- Compare ton requirements.txt ou pyproject.toml à une base de données de vulnérabilités
- Gratuit pour un usage basique, version payante pour la base de données complète
- Ne regarde que les dépendances, pas ton code

**pip-audit**

- Alternative à Safety, développé par les mainteneurs de pip
- Utilise la base de données PyPI Advisory
- 100% gratuit et open source
- Moins de vulnérabilités référencées que Safety Pro

**Trivy**

- Scanner multi-purpose : containers, code, dépendances, IaC (Terraform, Kubernetes...)
- Développé par Aqua Security
- Très complet pour les environnements Docker/K8s
- Peut remplacer Safety + scanner d'images Docker

**Snyk**

- Plateforme commerciale complète (code, dépendances, containers, IaC)
- Très bonne intégration GitHub/GitLab (PR automatiques pour fixer les vulnérabilités)
- Gratuit pour les projets open source, payant sinon
- Le plus user-friendly mais vendor lock-in

| Outil | Type | Coût | Intégration CI | Note |
|-------|------|------|----------------|------|
| **Bandit** | Code (statique) | Gratuit | Simple | 8/10 ✅ |
| **pip-audit** | Dépendances | Gratuit | Simple | 8/10 ✅ |
| **Safety** | Dépendances | Freemium | Simple | 7/10 |
| **Trivy** | Tout (containers, deps, IaC) | Gratuit | Moyen | 8/10 |
| **Snyk** | Tout | Freemium/Payant | Excellente | 7/10 |

**Choix : Bandit + pip-audit** — Combo gratuit et efficace. Bandit pour le code, pip-audit pour les dépendances. Si tu fais du Docker, ajoute Trivy.

**À surveiller :** **Semgrep** — un outil d'analyse statique très puissant avec des règles personnalisables. Peut remplacer Bandit avec plus de flexibilité. Gratuit pour les règles de base, payant pour les règles avancées.

---

## 📋 Tableau récapitulatif

| Catégorie | Outil choisi | Note | Justification |
|-----------|--------------|------|---------------|
| Linter | Ruff | 9/10 | Ultra-rapide, tout-en-un, standard moderne |
| Formatter | Ruff format | 9/10 | Même résultat que Black, instantané, intégré au linter |
| Type Checker | Pyright | 9/10 | Rapide, intégration VS Code native, mode strict complet |
| Tests | pytest | 9/10 | Standard de facto, syntaxe simple, écosystème de plugins |
| Security | Bandit + pip-audit | 8/10 | Combo gratuit : code + dépendances |

