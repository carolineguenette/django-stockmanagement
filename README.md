<div align="center">

<img src="./assets/img/logo.svg" alt="Logo Gestion de stocks" width="120" />

# Gestion de stocks

App Web Django — par [Caroline Guénette](mailto:cguenette@telus.net)

![Statut](https://img.shields.io/badge/Statut_du_projet-Phase_analyse_et_conception-purple.svg) ![Version](https://img.shields.io/badge/Implémentation-POC-purple.svg) ![Python](https://img.shields.io/badge/Python-3.11+-green.svg)  ![Django](https://img.shields.io/badge/Django-6.0.7-green.svg) ![Test](https://img.shields.io/badge/Test-À_venir-yellow.svg)

[![Schema](https://img.shields.io/badge/Gestion_du_projet-Jira-blue.svg)](https://solution-cg.atlassian.net/jira/software/c/projects/SD/list)  [![Schema](https://img.shields.io/badge/Schema_DB-LucidChart-F45D22.svg)](https://lucid.app/lucidchart/786327e6-745d-4881-95e1-39f3fdf33c66/edit?viewport_loc=4219%2C-3440%2C2860%2C1419%2C0_0&invitationId=inv_16c572fc-aaf2-4b0e-9e8f-636d2cf04698)

<h3>
  <a href="#présentation-du-projet">Projet</a> |
  <a href="#fonctionalités-clés">Fonctionalités clés</a> | 
  <a href="#spécifications-techniques">Spécifications techniques</a> | 
  <a href="#installation-configuration-et-tests-qualité">Installation, configuration et tests qualité</a>
</h3>

</div>

Consulter les documents de conception:

<h4>
  <a href="./docs/specifications.md">Cahier des charges</a> |
  <a href="./docs/dev-plan.md">Plan de développement</a> |
  <a href="./docs/data-security.md">Sécurité des données</a> | 
  <a href="./docs/database.md">Modèles et apps Django (database)</a>
</h3>

*Note sur Jira et LucidChart: il faut être connecté pour avoir accès aux informations en consultation (comptes gratuits).*

---

## Présentation du projet

Conception et développement d'une application web complète, moderne et professionnelle dédiée à la **gestion de stocks multi-entreprises**. *Ce projet met l'accent sur la sécurité des données, une architecture modulaire évolutive, l'expérience utilisateur et l'intégration de pratiques DevOps*

## Fonctionalités clés

1. **Gestion des utilisateurs et rôles :** Inscription, authentification, réinitialisation de mot de passe et attribution de droits d'accès spécifiques par entreprise.
2. **Catalogue produits :** Opérations CRUD complètes et module d'import/export au format CSV.
3. **Multi-entreprises :** Cloisonnement strict des données. Un utilisateur est affecté à un périmètre d'une ou plusieurs entreprises spécifiques.
4. **Internationalisation (i18n) :** Traduction de l'interface de l'application. Base de données conçue pour permettre l'implémentation de la traduction des données.
5. **Mouvements de stock :** Enregistrement des entrées et des sorties avec historisation, traçabilité et horodatage.
6. **Alertes de seuil critique :** Définition d'un seuil personnalisé par produit et notifications visuelles dans l'application lorsque les stocks sont insuffisants.
7. **Tableau de bord & Statistiques :** Visualisation graphique des quantités par catégorie et de l'évolution mensuelle grâce à **Chart.js**.
8. **Administration personnalisée :** Interface Django Admin optimisée avec des filtres et outils de recherche avancés pour piloter l'écosystème.

## Spécifications techniques

* **Langage & Framework :** Python 3.11+ / Django 6.0.7
* **Base de données :** MySQL (via `mysqlclient`). Code compatible avec PostgreSQL, SQLLite et MariaDB
* **Dépendances tierces :**
  * Gestion des variables d'environnement : `django-environ`
  * Framework de tests : `pytest-django`
  * Traitement d'images : `pillow` (Gestion des images Produit), `django-cleanup` (Suppression des fichiers médias orphelins)
  * Outils de développement: `django-browser-reload` (rechargement automatique), `ruff` (linter et formattage)
  * Gestion des fichiers CSV `django-import-export`

*La liste des dépendances sera mise à jour à mesure du développement.*

## Installation, configuration et tests qualité

```bash
# 1. Cloner le projet
git clone https://github.com/carolineguenette/django-stockmanagement
cd django-stockmanagement

# 2. Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Insertion du jeu de données de test
#A VENIR (`fixtures/initial_data.json`)
```

Les tests unitaires et fonctionnels sont exécutés automatiquement à chaque mise à jour sur la branche principale grâce à un workflow **GitHub Actions** basé sur `pytest`.

Pour lancer les tests localement :

```bash
pytest
```
