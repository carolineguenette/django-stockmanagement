<div align="center">

<img src="./assets/img/logo.svg" alt="Logo Gestion de stocks" width="120" />

# Gestion de stocks

App Web Django — par [Caroline Guénette](mailto:cguenette@telus.net)

<img src="https://img.shields.io/badge/Statut_du_projet-Révision_docs_de_conception-purple.svg" alt="Statut" /> ![Version](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/carolineguenette/django-stockmanagement/badges/django-stock-version.json) ![Coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/carolineguenette/django-stockmanagement/badges/django-stock-coverage.json) <img src="https://img.shields.io/badge/Python-3.11+-green.svg" alt="Python" /> <img src="https://img.shields.io/badge/Django-6.0.7-green.svg" alt="Django" />

[![Schema](https://img.shields.io/badge/Gestion_du_projet-Jira-blue.svg)](https://solution-cg.atlassian.net/jira/software/c/projects/SD/list) (lien vers Jira*) [![Schema](https://img.shields.io/badge/Schema_DB-LucidChart-F45D22.svg)](https://lucid.app/lucidchart/786327e6-745d-4881-95e1-39f3fdf33c66/view)) (lien vers LucidChart)

<h3>
  <a href="#projet">Projet</a> |
  <a href="#fonctionalités-cles">Fonctionalités clés</a> | 
  <a href="#specs">Spécifications techniques</a> | 
  <a href="#install">Installation, configuration et tests qualité</a>
</h3>

</div>

Consulter les documents de conception:
<h4>
  <a href="./docs/1-specifications.md">Cahier des charges</a> —
  <a href="./docs/2-conception.md">Conception</a> (<a href="./docs/4-data-security.md">Sécurité des données</a> |  
     <a href="./docs/6-database-models.md">Base de données</a>)
</h4>

**À noter que Jira est un peu capricieux pour les accès anonymes malgré une configuration en lecture adéquate.*

---

## Présentation du projet <a id="projet"></a>

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

## Spécifications techniques <a id="specs"></a>

* **Langage & Framework :** Python 3.11+ / Django 6.0.7
* **Base de données :** MySQL (via `mysqlclient`). Code compatible avec PostgreSQL, SQLLite et MariaDB
* **Dépendances tierces :**
  * Gestion des variables d'environnement : `django-environ`
  * Framework de tests : `pytest-django`
  * Traitement d'images : `pillow` (Gestion des images Produit), `django-cleanup` (Suppression des fichiers médias orphelins)
  * Outils de développement: `django-browser-reload` (rechargement automatique), `ruff` (linter et formattage)
  * Gestion des fichiers CSV `django-import-export`

*La liste des dépendances sera mise à jour à mesure du développement.*

## Installation, configuration et tests qualité <a href="install"></a>

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
