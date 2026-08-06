<div align="center">

<img src="../assets/img/logo.svg" alt="Logo Gestion de stocks" width="60" />

# Arborescence des fichiers

Projet Gestion de stocks — document de conception

![Statut](https://img.shields.io/badge/Statut_du_document-En_révision-purple.svg)

<h3>

[Custom RBAC](#rbac) | [CompanyMiddleware](#midleware) | [CompanyScopedManager](#manager) | [Permissions](#permissions) | [Roles](#roles) | [Tests de sécurité](#tests)

</h3>

</div>

Ce document présente l'arborescence projetée des fichiers composant le projet

[← Base de données](6-database-models.md) | [Sommaire](2-conception.md) |  [Plan de développement →](98-dev-plan.md)

---

```text
django-stock/
│
├── assets/                     # Ressources statiques du projet
│   ├── css/
│   ├── img/
│   └── js/
│
├── docs/
│   ├── conceptions.md
│   ├── data-security.md        # Fichier de conception sur la sécurité des données et le système d'accès
│   ├── database.md             # Fichier de conception sur la base de données
│   ├── dev-plan.md             # Explication des jalons de développement du projet et lien vers JIRA
│   ├── django-applications.md  # Fichier de conception sur les applications
│   ├── django-models.md        # Fichier de conception sur les modèles
│   ├── django-urls.md          # Fichier de conception sur les urls 
│   ├── django_stock.svg        # Image de la Database exportée de LucidChart
│   ├── project_structure.md    # Fichier de conception sur la structure du projet
│   ├── specifications.md       # Cahier des charges - 1er doc du projet
│   └── structure_directory.md  # Fichier de documentation de la structure du projet
│
├── locale/                     # Fichiers de traduction (i18n). fr, en, etc mais besoin aussi locale avec pays pour currency, affichage particulier (ex: ZIP en_US vs Postal Code en_CA), etc.
│
├── medias/                     # Fichiers multimédias téléversées à partir de l'interface UI (exclut dans le .gitignore)
│
├── src/                        # Code source du projet (apps core en détail: toutes les apps sont sur le même modèle)
│   ├── access/                 # Permissions métier, rôles et RBAC custom des employés
│   │   ├── models/
│   │   ├── services/
│   │   ├── decorators.py
│   │   ├── mixins.py
│   │   ├── validators.py
│   │   ├── admin.py
│   │   └── apps.py
│   │
│   ├── catalogue/              # Catalogue de produits, catégories, images et configurations produit
│   │
│   ├── company/                # Entreprises, locations et structure organisationnelle
│   │   ├── models/
│   │   ├── services/
│   │   ├── validators.py
│   │   ├── admin.py
│   │   └── apps.py
│   │
│   ├── config/                 # DOSSIER DE CONFIGURATION (Pas une application)
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py             # URLconf racine
│   │   └── wsgi.py
│   │
│   ├── core/                   # Socle technique partagé : modèles abstraits, templates, utils
│   │   ├── models/
│   │   ├── templates/
│   │   │   └── core/
│   │   ├── templatetags/
│   │   ├── views/
│   │   │
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   └── admin.py
│   │
│   ├── inventory/              # Stocks, mouvements, unités de mesure et transit
│   │
│   ├── reporting/              # Rapports company-scoped et rapports globaux owner
│   │
│   ├── scope/                  # Contexte compagnie courant, middleware et managers filtrants
│   │   ├── context.py          # Stockage du contexte compagnie courant
│   │   ├── exceptions.py       # Erreurs liées au scope courant
│   │   ├── managers.py         # CompanyScopedManager
│   │   ├── middleware.py       # CompanyMiddleware
│   │   ├── querysets.py        # CompanyScopedQuerySet
│   │   ├── mixins.py
│   │   └── apps.py
│   │
│   └── users/                  # Identité utilisateur et infrastructure d'authentification Django
│       ├── models/
│       ├── services/
│       │   └── owner_service.py
│       ├── forms/
│       ├── views/
│       ├── admin.py
│       └── apps.py
│
├── tests/                      # Dossier centralisé des tests automatisés. TODO: structure à définir
│   ├── htmlcov/
│   │
│   ├── __init__.py
│   ├── conftest.py             # Fixtures globales (Entreprises, Utilisateurs)
│   └── test_motor.py           # Un premier test pour valider que pytest-django fonctionne
│
├── .coveragerc
│
├── .env                        # Fichier de configuration des variables d'environnement (django-environ). Ignoré dans .gitignore (un fichier SAMPLE.env est fourni aussi)
│
├── .gitignore
│
├── manage.py
│
├── pytest.ini
│
├── README.md                   # Fichier de documentation du projet. Fait des liens vers ./docs/
│
└── requirements.txt
```