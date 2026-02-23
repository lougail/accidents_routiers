# Phase 2 : Stratégie Git & Branches - Questions de réflexion

## 1. Pourquoi protéger les branches ?

**Que se passerait-il sans protection ?**

Sans protection, plusieurs risques se présentent :

- **Erreurs humaines** : un développeur peut push directement du code non testé sur la branche de production (force push, commit accidentel, fichier sensible). C'est le risque le plus fréquent en pratique.
- **Perte de code** : un `git push --force` sur master peut écraser l'historique et le travail des autres développeurs, sans possibilité de récupération simple.
- **Code non validé en production** : sans obligation de passer par une PR et des status checks, du code buggé ou non conforme peut se retrouver déployé automatiquement en production.
- **Absence de traçabilité** : les commits directs ne passent pas par une revue de code, ce qui rend difficile le suivi de qui a introduit quoi et pourquoi.

La protection des branches force un workflow structuré (feature branch → PR → review → merge) qui agit comme un filet de sécurité contre ces risques.

## 2. Pourquoi Conventional Commits ?

**Avantages pour l'équipe :**

- **Historique lisible** : chaque commit indique clairement sa nature (feat, fix, refactor, etc.), ce qui permet de comprendre l'évolution du projet sans lire le code.
- **Communication** : un nouveau développeur sur le projet peut parcourir l'historique et comprendre rapidement ce qui a été fait, par qui, et dans quel but.
- **Revue de code facilitée** : dans une PR, les commits structurés permettent de reviewer les changements par catégorie (d'abord les fixes, puis les features, etc.).

**Avantages pour le versionnage automatique :**

- **Parsing automatique** : des outils comme `python-semantic-release` peuvent analyser les messages de commit et déterminer automatiquement le type de bump de version :
  - `feat:` → bump MINOR (0.1.0 → 0.2.0)
  - `fix:` → bump PATCH (0.1.0 → 0.1.1)
  - `BREAKING CHANGE` → bump MAJOR (0.1.0 → 1.0.0)
- **CHANGELOG automatique** : les commits sont regroupés par type et par version dans un fichier CHANGELOG.md généré automatiquement, ce qui documente chaque release sans effort manuel.
- **Releases GitHub** : le tag git et la release GitHub sont créés automatiquement avec les notes de version extraites des commits.

## 3. Différence entre develop et main ?

**Quand merger dans develop ?**

On merge dans `develop` à chaque fois qu'une feature branch est terminée et validée par la CI :

- Une fonctionnalité est implémentée (`feat/...`)
- Un bug est corrigé (`fix/...`)
- Du refactoring ou de la maintenance (`refactor/...`, `chore/...`)

`develop` est la branche d'intégration continue : elle accumule toutes les modifications validées individuellement. C'est ici qu'on vérifie que les différentes features fonctionnent ensemble.

**Quand merger dans main ?**

On merge `develop` dans `main` quand l'équipe décide de **sortir une nouvelle version**. C'est une décision métier, pas technique :

- Toutes les features prévues pour cette version sont intégrées dans `develop`
- La CI passe sur `develop` (code stable)
- L'équipe/le PO valide que c'est prêt pour la production

Le merge dans `main` déclenche automatiquement le semantic release (tag, CHANGELOG, GitHub Release) et potentiellement le déploiement en production.
