django-stock/
│
├── assets/                     # Ressources statiques du projet
│   ├── css/
│   ├── img/
│   └── js/
│
├── docs/
│   ├── data-security.md        # Fichier de conception sur la sécurité des données et le système de d'accès
│   ├── database.md             # Fichier de conception sur la base de données
│   ├── dev-plan.md             # Explication des jalons de développement du projet et lien vers JIRA
│   ├── specifications.md       # Cahier des charges - 1er doc du projet
│   └── structure_directory.md  # Fichier de documentation de la structure du projet
│
├── locale/                     # Fichiers de traduction (i18n)
│
├── medias/                     # Fichiers multimédias téléversées à partir de l'interface UI (exclut de github)
│
├── src/                        # Code source du projet
│   ├── catalogue/
│   ├── company/
│   ├── core/
│   ├── inventory/
│   ├── reporting/
│   ├── users/
│   │
│   ├── __init__.py
│   ├── settings.py
│   └── urls.py
│
├── tests/                      # Dossier centralisé des tests automatisés
│   ├── htmlcov/
│   │
│   ├── __init__.py
│   ├── conftest.py             # Fixtures globales (Entreprises, Utilisateurs)
│   └── test_motor.py           # Un premier test pour valider que pytest-django fonctionne
│
├── .coveragerc
│
├── .env
│
├── .gitignore
│
├── manage.py
│
├── pytest.ini
│
├── README.md
│
└── requirements.txt