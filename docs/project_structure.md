django-stock/
│
├── assets/                     # Ressources statiques du projet
│   ├── css/
│   ├── img/
│   └── js/
│
├── docs/
│   ├── data-security.md        # Fichier de conception sur la sécurité des données et le système d'accès
│   ├── database.md             # Fichier de conception sur la base de données
│   ├── dev-plan.md             # Explication des jalons de développement du projet et lien vers JIRA
│   ├── specifications.md       # Cahier des charges - 1er doc du projet
│   └── structure_directory.md  # Fichier de documentation de la structure du projet
│
├── locale/                     # Fichiers de traduction (i18n). fr, en, etc mais besoin aussi locale avec pays pour currency, affichage particulier, etc (ex: ZIP en_US vs Postal Code en_CA)
│
├── medias/                     # Fichiers multimédias téléversées à partir de l'interface UI (exclut dans le .gitignore)
│
├── src/                        # Code source du projet (apps catalogue en détail: toutes les apps sont sur le même modèle)
│   ├── catalogue/
│   │   ├── models/
│   │   ├── templates/
│   │   │   └── catalogue/
│   │   ├── templatetags/
│   │   │
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── views.py
│   │   └── admin.py
│   │
│   ├── company/
│   ├── config/                 # DOSSIER DE CONFIGURATION (Pas une application)
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py             # URLconf racine
│   │   └── wsgi.py
│   │
│   ├── core/                   # APPLICATION PARTAGÉE (master template, utils, etc)
│   ├── inventory/
│   ├── reporting/
│   └── users/
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