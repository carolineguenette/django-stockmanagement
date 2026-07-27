<div align="center">

<img src="../assets/img/logo.svg" alt="Logo Gestion de stocks" width="60" />

# Plan de développement

Projet Gestion de stocks — document de travail

![Statut](https://img.shields.io/badge/Statut_du_document-WIP-purple.svg)

<h3>
  <a href="#2-analyse-et-conception">Étape courante</a> | 
  <a href="#backlog">Backlog</a>
</h3>

</div>

# Introduction

Ce plan de développement fait office de feuille de route centralisant l'avancement du projet. Il permet aussi de prioriser les tâches selon une approche itérative (POC, MVP, V1).

### Jalons du projet


| Étape | Description                                                                                                                              |
| ------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
| POC    | Proof of Concept testant l'architecture multi-tenant et surtout l'isolation des données par entreprises                                 |
| MVP    | Minimal Viable Product mettant en oeuvre la valeur métier brute: gérer du stock et des mouvements d'inventaire de manière sécurisée |
| V1     | Première version incluant tous les éléments du cahier des charges                                                                     |
| VX     | Version future (fonctionnalités non prévues pour le développement pour le moment)                                                     |

Le développement entre MVP et V1 est jalonné par des sous-version (V0.1, V0.2, etc...)

## 1. Initialisation et infrastructure technique

* [X]  Configuration de l'environnement de développement (WSL Ubuntu, MySQL local, PyCharm Linux, GitHub).
* [X]  Configuration réseau avancée (Mode *mirrored* sur WSL, routage via domaine local `http://stock...`).
* [X]  Création de la base de données MySQL et validation des connecteurs Python (`mysqlclient`).
* [X]  Outillage de qualité de code et confort de dév (`django-browser-reload`, `ruff` pour le lint/format).
* [X]  Initialisation de l'architecture du projet Django (Dossier `./src`, configuration globale `settings.py` via `django-environ`).
* [X]  Création de l'application `users` et implémentation du modèle utilisateur personnalisé (`AbstractUser`).
* [X]  Création d'une application `catalogue` avec les modèles `Product` et `ProductImage`. Tests avec `pillow`; mise en place de signaux maison pour les image orphelines
* [X]  Implémentation du système d'internationalisation (i18n) de l'interface avec gestion des fichiers de traduction `.po` pour le Français (FR) et l'Espagnol (ES).
* [X]  Création d'une application `main` pour regrouper core de l'application (master templates). Création d'un `templatetags` `custom_translate_url` pour le pied de page avec le dropdown de sélection de la langues d'affichage de l'interface.
* [X]  Création, intégration et stylisation "à la main" (sans crispy-forms) du formulaire de connexion et du squelette de l'inscription (UI responsive, support des icônes SVG personnalisées).
* [X]  Implémentation des fondations graphiques pour le mode Clair (Light) et Sombre (Dark).

## 2. Analyse et conception

### Recherches

* [X]  Recherche sur les logiciels existants de Gestion de Stocks
* [X]  Recherche UX sur les logiciels de Gestion de Stocks

### Sécurité des données

* [X]  Analyse du fonctionnement des permissions et du système de rôles natif de Django
* [ ]  **EN COURS** — Documentation des choix d'architecture concernant les permissions (document  [docs/data-security.md](data-security.md)).

### Base de données

* [ ]  **EN COURS** — Modélisation de la base de données
* [ ]  **EN COURS** — Documentation des choix d'architecture concernant la base de données (document  [docs/database.md](database.md)).
* [ ]  **EN COURS** — [Schématisation de la base de données avec LucidChart](https://lucid.app/lucidchart/786327e6-745d-4881-95e1-39f3fdf33c66/edit?view_items=9Jse575XVdt2&page=0_0&invitationId=inv_16c572fc-aaf2-4b0e-9e8f-636d2cf04698)
* [ ]  Discussion avec des collègues / recueil d'avis externes

## 3. Proof of Concept (POC)

*Objectif : Valider la structure de données et l'étanchéité du cloisonnement des données.*

* [ ]  **Création des modèles de bases :**
  * [ ]  users.User (Absractuser)
  * [ ]  users.Role
  * [ ]  companies.Company
  * [ ]  companies.Location
  * [ ]  catalogue.Product
  * [ ]  catalogue.ProductConfig
* [ ]  **Insertion de données de test minimal** :
  * [ ]  1 utilisateur inactif (aucun accès), 1 utilisateur actif non superuser
  * [ ]  1 compagnie avec 2 locations (boutique, warehouse), 1 compagnie avec 1 location
  * [ ]  1 produit appartenant à la compagnie ayant 2 locations
  * [ ]  Permissions requis pour tester les mouvements d'inventaire
* [ ]  **Cloisonnement BDD :** Mettre en place les QuerySets personnalisés et les managers Django pour s'assurer qu'un utilisateur ne puisse requêter *que* l'entreprise à laquelle il est rattaché.
* [ ]  **Tests de sécurité du POC :**
  * [ ]  Configurer le fichier `pytest.ini`
  * [ ]  Écrire un premier test d'intégration factice qui valide l'infrastructure
  * [ ]  Écrire les premiers tests automatisés de périmètre pour prouver l'impossibilité d'une fuite de données inter-entreprises.

---

## Backlog

> [!WARNING]
> TODO: Besoin de révision

### Minimum Viable Product (MVP)

*Objectif : Mettre en œuvre la valeur métier brute de gestion de l'inventaire dans un environnement sécurisé.*

* [ ]  **Modélisation de l'infrastructure & des Flux :** Créer les modèles `Location` (dépôts/boutiques rattachés à une `Company`), `Stock` (liaison produit-lieu-quantité) et `Movement` (historique des flux).
* [ ]  **Contrôle d'accès (RBAC) :** Implémenter les permissions par rôle au niveau des vues de l'application (`data-security.md`).
* [ ]  **Authentification complète :** Rendre fonctionnel le formulaire d'inscription (`register`) et implémenter la réinitialisation de mot de passe sécurisée (`password-reset`).
* [ ]  **Formulaires métier sur mesure :** Développer le CRUD complet pour les produits avec des formulaires HTML/CSS.
* [ ]  **Mouvements de stock transactionnels :** Créer la vue des mouvements avec traitement dynamique (entrées/sorties) encapsulé dans des transactions MySQL pour sécuriser les calculs de volumes de stock.

### Version Finale (V1)

*Objectif : Finaliser le cahier des charges, optimiser les performances et automatiser les processus.*

* [ ]  **Système d'alertes :** Développer les notifications in-app automatiques basées sur la condition `Stock.quantite < Product.seuil_alerte`.
* [ ]  **Import/Export :** Intégrer l'échange de catalogues au format CSV via `django-import-export`.
* [ ]  **Tableau de bord :** Intégrer Chart.js pour générer les graphiques d'évolution mensuelle et de répartition par catégorie.
* [ ]  **Optimisation MySQL :** Auditer les vues et injecter systématiquement `select_related` et `prefetch_related` pour éliminer le problème des requêtes N+1.
* [ ]  **Nettoyage automatique :** Ajouter `django-cleanup` pour supprimer les fichiers d'images de produits orphelins sur le disque.
* [ ]  **CI/CD :** Configurer `pytest.ini` et implémenter le workflow GitHub Actions pour exécuter la suite de tests automatisés à chaque push/PR.
* [ ]  **Livrables :** Générer le jeu de données initial (`fixtures/initial_data.json`) et finaliser la documentation utilisateur dans le `README.md`.

### Outillage, CI et initialisation

* [ ]  Ajouter les dépendances clés : `pytest-django`, `django-import-export` et `django-cleanup` (pour remplacer les signaux maison de `ProductImage`)
* [ ]  Mettre en place le workflow GitHub Actions minimal (déclenchement de `pytest` sur chaque push et PR) pour tester automatiquement chaque brique future

### Cœur métier : Modèles cibles, Multi-entreprises & Catégories

* [ ]  **Définition du modèle central :** Création du modèle `Company` (Entreprise/Warehouse) pour valider l'architecture globale avec le mentor
* [ ]  **Modélisation du Catalogue :** Ajouter le modèle `Category` et amender `Product` pour intégrer la notion de catégories
* [ ]  **Modélisation de l'infrastructure :** Créer le modèle `Location` (nom, adresse, type dépôt/boutique) explicitement rattaché à une `Company`
* [ ]  **Modélisation des Flux :** Créer les modèles `Stock` (produit, lieu, quantité) et `Movement` (produit, lieu source/destination, quantité, date, raison)
* [ ]  **Périmètre Utilisateur :** Concevoir la table d'affectation `User ↔ Company` (avec gestion des droits par entreprise) pour valider le POC de sécurité
* [ ]  Générer les migrations, implémenter les méthodes `__str__` et configurer l'interface d'administration Django de base pour ces entités

### Périmètre, Sécurité & Filtrage

* [ ]  Mettre en place le filtrage systématique au niveau des requêtes (QuerySets personnalisés, Mixins de vues) : un utilisateur ne doit voir et modifier que les données des entreprises auxquelles il est rattaché
* [ ]  Implémenter les permissions par rôle (RBAC)
* [ ]  Écrire les premiers tests de périmètre et de cloisonnement inter-entreprises

### Catalogue & Authentification

* [ ]  Développer le CRUD complet pour les produits en utilisant les formulaires natifs Django avec gestion HTML/CSS "manuelle" (Contrôle total du rendu)
* [ ]  Intégrer l'import/export CSV du catalogue via `django-import-export`
* [ ]  Finaliser l'authentification : implémenter les fonctionnalités de `register` et de `password-reset` (nettoyage des `# TODO Temporaire` dans `src/urls.py`)

### Mouvements & Alertes transactionnelles

* [ ]  Créer la vue des mouvements de stock avec un formulaire dynamique (gestion des entrées, sorties et transferts)
* [ ]  Garantir la mise à jour transactionnelle sécurisée des quantités dans le modèle `Stock` lors d'un mouvement
* [ ]  Développer le système d'alertes de seuil critique (notifications in-app dès que `Stock.quantite < Product.seuil_alerte`)

### Tableau de bord & Optimisation BDD

* [ ]  Concevoir le tableau de bord principal avec intégration de Chart.js (graphiques des quantités par catégorie et évolution mensuelle)
* [ ]  Optimiser les requêtes MySQL en injectant systématiquement `select_related` et `prefetch_related` pour éliminer le risque de performance BDD (problème des requêtes N+1)

### Finitions & Livrables finaux

* [ ]  Personnaliser l'interface d'administration (filtres avancés, moteurs de recherche internes, affichages des colonnes d'audit)
* [ ]  Générer le jeu de données d'exemple attendu dans `fixtures/initial_data.json`
* [ ]  Étoffer la suite de tests unitaires et fonctionnels sous `pytest`
* [ ]  Finaliser la documentation du README (guide complet d'installation, commandes utiles, scénarios d'exemples)
