# 📚 Phase 0 : Veille Technologique

---

## 📝 Missions de veille


### Mission 1 : Comprendre CI/CD

---

### 1. Qu'est-ce que la Continuous Integration ?

**Quels problèmes résout-elle ?**

La CI permet d'intégrer en continu le travail des différents collaborateurs sur un repo. À chaque commit / push, le code est testé avant d'être mergé automatiquement.

Cela évite le **"integration hell"** : chacun code dans son coin pendant de longues périodes, et le jour où il faut tout merge pour mettre en prod, c'est le calvaire. La CI permet de faire des intégrations au fur et à mesure ; ainsi, quand une nouvelle intégration casse le code, on sait directement quelle partie est problématique.

Par ailleurs, cela permet de tester le code dans un environnement standardisé à chaque push, ce qui résout le problème du *"ça marche sur ma machine mais pas celle des autres"*.

**Quels sont les principes clés ?**

- Maintenir un **repo unique** avec un système de versioning.
- Chaque commit déclenche un **workflow automatique** qui build et exécute les tests. Les vérifications ne doivent pas être manuelles.
- Dès qu'un build casse, la **priorité** devient de réparer le problème avant de continuer tout autre développement.

**3 exemples d'outils de CI :**

- GitHub Actions
- GitLab CI/CD
- Jenkins

---

### 2. Qu'est-ce que le Continuous Deployment / Delivery ?

**Différence entre Continuous Delivery et Continuous Deployment**

- **Continuous Delivery :** on automatise toute la pipeline jusqu'au déploiement sur l'environnement de staging, mais la dernière étape de mise en production doit toujours être validée et approuvée par un membre de l'équipe.
- **Continuous Deployment :** on automatise toute la pipeline CI/CD jusqu'au déploiement sur l'environnement de production. Tout est automatisé, du commit du dev à la mise en production de l'appli.

> Pour résumer — Delivery = *"on peut déployer à tout moment"* | Deployment = *"on déploie en continu"*

**Risques**

- **Déployer un bug en production :** le déploiement étant automatisé, il faut être certain d'avoir des tests solides avec une bonne couverture de code, sinon on automatise la livraison de bugs.
- **Complexité de mise en place :** il faut investir du temps et des ressources pour mettre en place tout le système (pipelines, environnements de staging, monitoring, rollback…).
- **Contexte inadapté :** dans certains domaines (banques, santé…), la validation humaine reste impérative (conformité légale, approbation métier…). Dans ce cas, le Continuous Delivery est plus adapté.

**Bénéfices**

- **Rapidité de mise en production :** les utilisateurs profitent plus vite des nouvelles fonctionnalités et des corrections, et les développeurs obtiennent des feedbacks rapides.
- **Déploiements atomiques :** chaque déploiement contient peu de changements, ce qui permet d'identifier facilement ce qui a cassé l'application.
- **Réduction du travail répétitif :** les devs n'ont plus à gérer manuellement la mise en production.

---

### 3. Pourquoi CI/CD est important ?

**Impact sur la qualité du code**

Tout le code est testé à chaque commit (tests unitaires, tests d'intégration, linting, vérification de la couverture du code). Rien n'arrive en production sans avoir subi tous ces tests. Cela sécurise la mise en production : si un développeur introduit une régression ou un bug, il est détecté immédiatement et non pas trois semaines plus tard lors de l'exécution manuelle des tests. On sait aussi précisément quelle partie du code a créé le problème.

Par ailleurs, cela incite l'équipe à avoir des tests complets et à jour. Les tests deviennent une nécessité concrète, car un code mal testé peut bloquer tout le pipeline.

**Impact sur la vitesse de développement**

Sans CI/CD, une fois qu'il a fini son code, le dev doit lancer les tests à la main, préparer le build, copier les fichiers vers le serveur, vérifier que tout tourne en prod… Le but du CI/CD est d'automatiser tout ça : le dev commit et push son code, la pipeline s'exécute, et si tout est OK le code est déployé automatiquement en production. Le dev peut immédiatement passer à sa tâche suivante, sans avoir à gérer les tests et la mise en prod.

**Impact sur la collaboration en équipe**

Le CI/CD évite que des devs se retrouvent isolés sur des sujets séparés et que les projets divergent. On push et merge au fur et à mesure, ce qui assure que toutes les personnes qui travaillent sur le projet ont le code à jour en permanence et que ce qu'ils développent s'intègre facilement à ce qui est déjà en place.

Cela permet aussi d'avoir un **standard commun et objectif** pour la validation du code. Ce n'est plus subjectif ou conditionné par ton statut dans la boîte : tout le code passe par la pipeline, c'est elle qui a valeur de vérité. Soit elle valide ton code, soit ça casse et toute l'équipe doit corriger ensemble le problème. Cela favorise la culture de la responsabilité partagée.

---

### Mission 2 : Maîtriser uv

---

### 1. Qu'est-ce que uv ?

**En quoi est-ce différent de pip/poetry/pipenv ?**

- **pip** est juste un installateur de paquets. Il ne gère ni les environnements virtuels, ni les lockfiles, ni la résolution intelligente des conflits de versions. C'est l'outil de base, mais il faut le combiner avec d'autres outils (venv, pip-tools...) pour avoir un workflow complet.

- **pipenv** a été la première tentative d'unifier pip + virtualenv + lockfile dans un seul outil. Il introduit le Pipfile.lock pour des installations reproductibles. Mais il est lent, et son développement a stagné.

- **poetry** est devenu le standard de facto : il gère tout (dépendances, environnements, build, publication sur PyPI) avec une bonne UX. Son défaut : il utilise son propre format (pyproject.toml avec des sections [tool.poetry]) et peut être lent sur les gros projets.

- **uv** est développé par Astral (les créateurs de Ruff) et réécrit tout en Rust. Il remplace pip, venv, pip-tools et même pyenv dans un seul binaire ultra-rapide. Contrairement à poetry, il utilise les standards Python (PEP 621) sans sections propriétaires.

> Pour résumer — pip = installateur basique | pipenv = tentative d'unification (abandonnée) | poetry = solution complète mais lente | uv = tout-en-un rapide et standard

**Quels sont les avantages ?**

- **Vitesse** : écrit en Rust avec une résolution des dépendances parallélisée, uv est 10 à 100 fois plus rapide que pip ou poetry. Sur un gros projet, uv sync prend quelques secondes là où poetry install peut prendre plusieurs minutes.

- **Tout-en-un** : uv peut installer Python lui-même (uv python install 3.12), créer des environnements virtuels, installer les dépendances et exécuter des commandes. Plus besoin de jongler entre pyenv, venv et pip.

- **Standards Python** : uv utilise pyproject.toml au format PEP 621, le standard officiel. Pas de format propriétaire, donc facile à migrer vers ou depuis un autre outil.

- **Reproductibilité** : le fichier uv.lock garantit que tous les développeurs et la CI installent exactement les mêmes versions, à l'octet près.

- **Drop-in replacement** : uv pip install requests fonctionne exactement comme pip install requests. On peut migrer progressivement sans tout casser.

---

### 2. Comment uv fonctionne avec pyproject.toml ?

**Structure du fichier**

Le pyproject.toml est le fichier de configuration standard pour les projets Python (PEP 621). Il contient trois sections principales :

- [project] : les métadonnées du projet (nom, version, description, version Python requise, dépendances)
- [project.optional-dependencies] : les dépendances optionnelles groupées par usage (dev, test, docs...)
- [build-system] : le backend utilisé pour construire le package

**Gestion des dépendances (séparé par sections)**

```toml
[project]
name = "mon-projet"
version = "0.1.0"
requires-python = ">=3.10"

# Dépendances de production (installées par défaut)
dependencies = [
    "fastapi>=0.100.0",
    "pandas>=2.0.0",
]

[project.optional-dependencies]
# Dépendances de dev : uv sync --extra dev
dev = [
    "pytest>=7.0.0",
    "ruff>=0.1.0",
]
# Dépendances de docs : uv sync --extra docs
docs = [
    "mkdocs>=1.5.0",
]
```

Pour installer les dépendances de prod + dev : uv sync --extra dev

**Build backend**

Le build backend est l'outil qui transforme ton code source en package installable (.whl, .tar.gz). Les plus courants :

- **hatchling** : moderne, rapide, recommandé par défaut
- **setuptools** : l'historique, encore très utilisé
- **flit-core** : minimaliste, pour les packages simples

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

---

### 3. Comment utiliser uv dans GitHub Actions ?

**Installation**

Astral fournit une action officielle astral-sh/setup-uv qui installe uv dans le runner :

```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v3
```

Pas besoin d'installer Python séparément : uv peut le faire lui-même si nécessaire.

**Cache des dépendances**

Pour éviter de re-télécharger les dépendances à chaque run, on met en cache le dossier ~/.cache/uv. La clé du cache est basée sur le hash du lockfile : si les dépendances changent, le cache est invalidé.

```yaml
- name: Cache uv dependencies
  uses: actions/cache@v4
  with:
    path: ~/.cache/uv
    key: ${{ runner.os }}-uv-${{ hashFiles('uv.lock') }}
```

**Exécution de commandes**

```yaml
- name: Install dependencies
  run: uv sync --frozen

- name: Run tests
  run: uv run pytest

- name: Run linter
  run: uv run ruff check .
```

- uv sync --frozen : installe les dépendances exactes du lockfile sans le mettre à jour (important en CI pour la reproductibilité)
- uv run <cmd> : exécute une commande dans l'environnement virtuel sans avoir besoin de l'activer manuellement

---

### Mission 3 : Comprendre Semantic Release

---

### 1. Qu'est-ce que le versionnage sémantique (SemVer) ?

**Format MAJOR.MINOR.PATCH**

Le versionnage sémantique (ou SemVer) est une convention pour numéroter les versions d'un logiciel de manière cohérente et compréhensible. Le format est X.Y.Z :

- **X (MAJOR)** : la version majeure. Elle change quand on introduit des modifications incompatibles avec les versions précédentes.
- **Y (MINOR)** : la version mineure. Elle change quand on ajoute des fonctionnalités tout en restant rétrocompatible.
- **Z (PATCH)** : le correctif. Il change quand on corrige des bugs sans modifier l'API.

Par exemple, 2.4.1 signifie : deuxième version majeure, quatrième ajout de fonctionnalités depuis la v2, premier correctif depuis la v2.4.

**Quand bumper chaque niveau ?**

- On **bump le PATCH** (1.0.0 → 1.0.1) quand on corrige un bug sans changer le comportement de l'API. Les utilisateurs peuvent mettre à jour sans rien modifier dans leur code.

- On **bump le MINOR** (1.0.0 → 1.1.0) quand on ajoute une nouvelle fonctionnalité qui n'impacte pas le code existant. Le code des utilisateurs reste compatible.

- On **bump le MAJOR** (1.0.0 → 2.0.0) quand on fait un changement qui casse la compatibilité : renommage de fonction, suppression d'un paramètre, changement de comportement par défaut... Les utilisateurs devront potentiellement adapter leur code.

> Règle importante : quand on bump un niveau, on remet les niveaux inférieurs à zéro. Exemple : 1.4.3 → 2.0.0 (et non 2.4.3).

---

### 2. Qu'est-ce que Conventional Commits ?

**Format des messages**

Conventional Commits est une convention pour structurer les messages de commit de manière standardisée. Le format est :

```
<type>(<scope>): <description>

[corps optionnel]

[footer optionnel]
```

Exemples :
- feat(auth): add login with Google
- fix(api): handle null response from server
- docs: update README with installation steps

Le scope (entre parenthèses) est optionnel et indique la partie du ode concernée.

**Types de commits (feat, fix, etc.)**

- **feat** : nouvelle fonctionnalité
- **fix** : correction de bug
- **docs** : modification de la documentation uniquement
- **style** : formatage, point-virgules manquants... (pas de changement de logique)
- **refactor** : refactorisation du code (ni feature, ni fix)
- **test** : ajout ou modification de tests
- **chore** : maintenance, mise à jour de dépendances, config...

**Impact sur le versionnage**

C'est là que Conventional Commits devient puissant : le type de commit détermine automatiquement quel niveau de version bumper.

- fix: → bump **PATCH** (1.0.0 → 1.0.1)
- feat: → bump **MINOR** (1.0.0 → 1.1.0)
- feat!: ou BREAKING CHANGE: dans le footer → bump **MAJOR** (1.0.0 → 2.0.0)

Les autres types (docs, style, refactor, test, chore) ne déclenchent pas de nouvelle version par défaut.

> L'intérêt : on peut automatiser entièrement le versionnage. Un outil comme python-semantic-release lit l'historique des commits, détermine le bon niveau de version et crée la release automatiquement.

---

### 3. Comment python-semantic-release fonctionne ?

**Configuration dans pyproject.toml**

python-semantic-release se configure dans le pyproject.toml avec la section [tool.semantic_release] :

```toml
[tool.semantic_release]
version_variable = "src/__init__.py:__version__"
version_toml = ["pyproject.toml:project.version"]
branch = "main"
upload_to_pypi = false
upload_to_release = true
build_command = "uv build"
```

- version_variable : où mettre à jour la version dans le code
- version_toml : où mettre à jour la version dans pyproject.toml
- branch : la branche sur laquelle déclencher les releases
- upload_to_release : créer une release GitHub avec les assets

**Génération du CHANGELOG**

python-semantic-release génère automatiquement un CHANGELOG.md à partir des commits. Il regroupe les commits par type et par version :

```markdown
## v1.2.0 (2024-01-15)

### Features
- Add user authentication (feat(auth): add login endpoint)

### Bug Fixes
- Fix crash on empty input (fix(parser): handle null values)
```

Le changelog est mis à jour à chaque release, ce qui documente automatiquement l'évolution du projet.

**Création des releases GitHub**

Quand python-semantic-release s'exécute (généralement dans une GitHub Action), il :

1. Analyse les commits depuis la dernière release
2. Détermine le nouveau numéro de version selon les types de commits
3. Met à jour les fichiers de version (pyproject.toml, __init__.py...)
4. Met à jour le CHANGELOG
5. Crée un commit et un tag Git
6. Crée une release GitHub avec les notes de version

Le tout automatiquement, sans intervention humaine.

---

### Mission 5 : MkDocs & GitHub Pages (bonus)

---

### 1. Comment MkDocs génère de la documentation ?

MkDocs est un générateur de sites statiques conçu spécifiquement pour la documentation. Tu écris tes docs en Markdown, et MkDocs les transforme en un site web navigable.

**Structure d'un projet MkDocs :**

```
mon-projet/
├── docs/
│   ├── index.md          # Page d'accueil
│   ├── installation.md   # Autres pages
│   └── api/
│       └── reference.md
├── mkdocs.yml            # Configuration
└── src/                  # Ton code Python
```

**Configuration minimale (mkdocs.yml) :**

```yaml
site_name: Mon Projet
theme:
  name: material    # Theme Material (le plus populaire)
nav:
  - Accueil: index.md
  - Installation: installation.md
  - API: api/reference.md
```

**Commandes principales :**

- mkdocs serve : lance un serveur local avec hot-reload
- mkdocs build : génère le site statique dans site/

---

### 2. Comment déployer sur GitHub Pages ?

GitHub Pages héberge gratuitement des sites statiques. Deux options :

**Option 1 : Commande manuelle**

```bash
mkdocs gh-deploy
```

Cette commande build le site et le push sur la branche gh-pages automatiquement.

**Option 2 : GitHub Actions (recommandé)**

```yaml
name: Deploy docs
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv sync --extra docs
      - run: uv run mkdocs gh-deploy --force
```

Le site sera accessible à https://<username>.github.io/<repo>/

---

### 3. Qu'est-ce que mkdocstrings ?

mkdocstrings est un plugin MkDocs qui génère automatiquement la documentation de ton API à partir des docstrings de ton code Python.

Au lieu d'écrire manuellement la doc de chaque fonction, tu écris dans ton Markdown :

```markdown
# API Reference

::: mon_module.ma_fonction
```

Et mkdocstrings va chercher la fonction dans ton code, lire sa docstring, ses paramètres, ses types, et générer une belle page de documentation.

**Configuration :**

```yaml
plugins:
  - mkdocstrings:
      handlers:
        python:
          options:
            show_source: true
            show_signature_annotations: true
```

**Exemple de docstring qui sera parsée :**

```python
def calculate_sum(a: int, b: int) -> int:
    """Calcule la somme de deux nombres.

    Args:
        a: Premier nombre
        b: Deuxième nombre

    Returns:
        La somme de a et b
    """
    return a + b
```

> L'intérêt : ta doc API est toujours à jour car elle est générée directement depuis le code. Plus de doc obsolète qui ne correspond plus au code.

