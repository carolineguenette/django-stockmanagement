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
│   ├── settings.py
│   └── urls.py
│
├── tests/                      # Dossier centralisé des tests automatisés
│   ├── __init__.py
│   ├── conftest.py             # Contiendra vos futures fixtures globales (Entreprises, Utilisateurs)
│   └── test_infrastructure.py  # Votre premier test bidon
│
├── .env
│
├── .gitignore
│
├── manage.py
│
├── README.md
│
└── requirements.txt