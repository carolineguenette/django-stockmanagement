<div align="center">%

<img src="../assets/img/logo.svg" alt="Logo Gestion de stocks" width="60" />

# Arborescence des fichiers

Projet Gestion de stocks — document de conception

![Statut](https://img.shields.io/badge/Statut_du_document-En_cours_de_rédaction-purple.svg)

</div>

Ce document présente l'arborescence projetée des fichiers composant le projet.

[← Système d'inventaire](7-inventory-system.md) | [Sommaire](2-conception.md) |  [Plan de développement →](9-dev-plan.md)

```tree
django-stock/
│
├── assets/                     # Ressources statiques du projet
│   ├── css/
│   ├── img/
│   └── js/
│
├── docs/
│   ├── 1-specifications.md         # Cahier des charges - 1er doc du projet
│   ├── 2-conception.md             # Sommaire et table des matieres globale
│   ├── 3-choices-and-analysis.md   # Analyse et justifications techniques des choix réalisés
│   ├── 4-data-security.md          # Sécurité des données et système de contrôle d'accès RBAC
│   ├── 5-django-apps-and-urls.md   # Descriptions des applications et urls
│   ├── 6-database-models.md        # Base de données
│   ├── 7-project-structure.md      # Arborescence des fichiers
│   ├── 8-dev-plan.md               # Explication des jalons de développement du projet, gestion de projet (JIRA), automatisation
│   ├── schema_database.pdf         # Database exportée de LucidChart
│   └── schema_database.svg         # Database exportée de LucidChart
│
├── locale/                     # Fichiers de traduction (i18n)
│   ├── en_CA                   # répertoire sans pays : 90$ des traductions
│   ├── en_US                   # répertoire avec pays : les 10% de différences restants
│   ├── en                      #    ex: ZIP Code vs Postal Code, etc.
│   ├── fr_CA
│   ├── fr_FR
│   └── fr
│
├── medias/                     # Fichiers multimédias téléversées à partir de l'interface UI (exclut dans le .gitignore)
│
├── src/                        # Code source du projet (apps core en détail: toutes les apps sont sur le même modèle)
│   ├── access/                 # Permissions métier, rôles et RBAC custom des employés
│   │   ├── models/
│   │   │   ├── permission.py (Permission)
│   │   │   ├── role.py (Role)
│   │   │   └── role_permissions.py (RolePermission)
│   │   ├── services/
│   │   │   └── company_access_service.py (CompanyAccessService)
│   │   ├── admin.py
│   │   ├── apps.py (AccessConfig)
│   │   ├── auth_backend.py   (CompanyRBACBackend)
│   │   ├── choices.py        (PermissionContextChoices)
│   │   ├── decorators.py     (ex: @require_company_permission)
│   │   ├── mixins.py         (ex: CompanyRequiredMixin)
│   │   └── validators.py
│   │
│   ├── catalogue/              # Catalogue de produits, catégories, images et configurations produit
│   │   ├── models/
│   │   │   ├── product.py (Product)
│   │   │   ├── product_image.py (ProductImage)
│   │   │   ├── productmodel.py (ProductModel)
│   │   │   ├── productconfig.py (ProductConfig)
│   │   │   ├── productpackaging.py (ProductPackaging)
│   │   │   ├── productattribute.py (ProductAttribute)
│   │   │   ├── category.py (Category)
│   │   │   └── attribute.py (Attribute)
│   │   ├── admin.py
│   │   ├── apps.py (CatalogueConfig)
│   │   ├── signals.py
│   │   └── urls.py
│   │
│   ├── company/                # Entreprises, locations et structure organisationnelle
│   │   ├── models/
│   │   │   ├── company.py (Company)
│   │   │   ├── location.py (Location)
│   │   │   ├── location_type.py (LocationType)
│   │   │   └── uom.py (Uom)
│   │   ├── services/
│   │   │   └── company_lifecycle_service.py (CompanyLifecycleService)
│   │   ├── admin.py
│   │   ├── apps.py (CompanyConfig)
│   │   └── validators.py
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
│   │   │   └── abstract_audit.py (AbstractAudit)
│   │   ├── templates/
│   │   │   └── core/
│   │   ├── templatetags/
│   │   │   └── i18n_urls.py
│   │   ├── views/
│   │   ├── admin.py
│   │   ├── apps.py (CoreConfig)
│   │   ├── context_processors.py
│   │   └── middleware.py (AuditUserMiddleware)
│   │
│   ├── inventory/              # Stocks, mouvements, unités de mesure et transit
│   │   ├── models/
│   │   │   ├── stock.py (Stock)
│   │   │   ├── movement.py (Movement)
│   │   │   ├── movement_reason.py (MovementReason)
│   │   │   ├── transit.py (Transit)
│   │   ├── admin.py
│   │   ├── apps.py (InventoryConfig)
│   │   └── urls.py
│   │
│   ├── reporting/              # Rapports company-scoped et rapports globaux owner
│   │   ├── admin.py
│   │   ├── apps.py (ReportingConfig)
│   │   └── urls.py
│   │
│   ├── scope/                  # Contexte compagnie courant, middleware et managers filtrants
│   │   ├── managers/
│   │   │   ├── company_scoped_manager.py (CompanyScopedManager)
│   │   │   ├── companies_scoped_manager.py (CompaniesScopedManager)
│   │   │   └── unscoped_manager.py (UnscopedManager)
│   │   ├── models/
│   │   │   └── abstract_companyowned.py (CompanyOwned)
│   │   ├── admin.py
│   │   ├── apps.py (ScopeConfig)
│   │   ├── context.py (RequestScope, ScopeMode)     # Stockage du contexte compagnie courant
│   │   ├── exceptions.py (MissingCompanyScope, MissingCompaniesScope)    # Erreurs liées au scope courant
│   │   └── middleware.py (CompanyMiddleware)
│   │
│   └── users/                  # Identité utilisateur et infrastructure d'authentification Django
│       ├── forms/
│       ├── models/
│       │   ├── user.py (User)
│       │   ├── user_hierarchy.py (UserHierarchy)
│       │   ├── user_role.py (UserRole)
│       │   └── user_role_log.py (UserRoleLog)
│       ├── services/
│       │   └── owner_service.py (OwnerService)
│       ├── views/
│       ├── admin.py
│       ├── apps.py (UsersConfig)
│       └── middleware.py (RegionalLocaleMiddleware)
│
├── tests/                      # Dossier centralisé des tests automatisés. TODO: structure à définir
│   ├── conftest.py
│   ├── htmlcov/
│   ├── test_access/
│   ├── test_catalogue/
│   ├── test_company/
│   ├── test_inventory/
│   ├── test_scope/
│   ├── test_users/
│   ├── conftest.py             # Fixtures globales (Entreprises, Utilisateurs)
│   └── test_motor.py           # Un premier test pour valider que pytest-django fonctionne
│
├── .coveragerc
├── .env                        # Fichier de configuration des variables d'environnement (django-environ). Ignoré dans .gitignore (un fichier SAMPLE.env est fourni aussi)
├── .gitignore
├── manage.py
├── pytest.ini
├── README.md                   # Fichier de documentation du projet. Fait des liens vers ./docs/
└── requirements.txt
```