<div align="center">

<img src="./assets/img/logo.svg" alt="Logo Gestion de stocks" width="120" />

# Gestion de stocks

App Web Django — par [Caroline Guénette](mailto:cguenette@telus.net)

<h3>
  <a href="#%EF%B8%8F-stack-technique--dépendances">Stack technique</a> | 
  <a href="#-fonctionnalités-clés-objectifs">Fonctionnalités clés</a> | 
  <a href="#-devops--qualité">Dev Ops</a>
</h3>

</div>

> **Statut du projet :** ⚠️ En cours de développement | [Plan de développement](#️-plan-de-développement--task-list)

---

## 🎯 Vision du projet

Application web moderne, sécurisée et multilingue de gestion d'inventaire multi-entreprises. L'application est conçue pour permettre à des propriétaires de suivre en temps réel leurs flux de stocks, d'analyser leurs performances via un tableau de bord statistique et de gérer finement les accès de leurs collaborateurs grâce à un système de rôles avancé (RBAC).

## 🛠️ Stack Technique & Dépendances

![Python](https://img.shields.io/badge/Python-3.11+-green.svg)   ![Django](https://img.shields.io/badge/Django-6.0.7-green.svg)

* **Framework Back-End :** Django 6.0.7 sur Python 3.11+
* **Base de Données :** MySQL (via `mysqlclient`)
* **Qualité & Formatage :** Ruff (Linter & Formatter)
* **Gestion Environnementale :** `django-environ` (Configuration via fichier `.env`)
* **Outils de Développement :** `django-browser-reload` (Rechargement à chaud)
* **Traitement d'Images :** Pillow (Gestion des visuels produits)

## ✨ Fonctionnalités clés (Objectifs)

### 👤 Gestion des Utilisateurs & Rôles

* **Modèle Utilisateur Personnalisé :** Extension d'`AbstractUser` pour intégrer dynamiquement le choix de la langue par profil.
* **Authentification Complète :** Vues Django de Connexion/Déconnexion opérationnelles avec templates dédiés et icônes SVG adaptatives (Mode clair/sombre).
* **Contrôle d'Accès Granulaire (RBAC) :** Cloisonnement par rôles et par entreprises (Spécifications disponibles dans la [Documentation de l'architecture des rôles](./docs/architecture-roles.md)).

### 🌍 Internationalisation (i18n) & Localisation

* **Système Multilingue Solide :** Intégration complète via `LocaleMiddleware` et routage par `i18n_patterns`.
* **Traductions Disponibles :** Anglais nativement et support du Français (FR) et de l'Espagnol (ES) compilé, incluant un sélecteur de langue dynamique et le templatetag `i18n_urls`.
* Gestion des devises et préférences d'affichages (locales)

### 📦 Catalogue Produits

* **Modélisation Avancée :** Modèle `Product` incluant un index SKU unique, validation stricte des prix (≥ 0) et horodatage d'audit complet (`created_at`, `updated_at`, `created_by`, `updated_by`).
* **Gestion des Médias :** Modèle `ProductImage` avec processus automatique de renommage des fichiers (SKU + UUID) et signaux Django actifs pour le nettoyage des fichiers d'images orphelins sur le disque.
* *En cours :* Finalisation des vues CRUD du catalogue et de la fonctionnalité d'import/export CSV.

### 📉 Logique d'Inventaire & Reporting

* **Cœur Métier :** Modélisation future des entités `Site`, `Stock` et `Movement` (entrées/sorties historisées).
* **Alertes de Seuil :** Système d'alerte critique paramétrable par produit avec notifications internes.
* **Tableau de Bord :** Interface statistique dynamique exploitant Chart.js pour l'analyse des mouvements de stocks.

## 🚀 DevOps & Qualité

* **Intégration Continue (CI) :** Pipeline GitHub Actions planifié pour l'exécution automatique des tests à chaque commit.
* **Suite de Tests :** Tests unitaires et fonctionnels (pytest-django) en cours de rédaction (fondations prêtes).
* **Données de Démo :** Jeux de données d'exemple (`fixtures/initial_data.json`) prévus pour l'initialisation rapide du projet.

---

## 🗺️ Plan de développement & Task List

### Jalon 0 — Outillage, CI & Initialisation

* [ ]  Ajouter les dépendances clés : `pytest-django`, `django-import-export` et `django-cleanup` (pour remplacer les signaux maison de `ProductImage`)
* [ ]  Configurer le fichier `pytest.ini` et écrire un premier test d'intégration factice qui valide l'infrastructure
* [ ]  Mettre en place le workflow GitHub Actions minimal (déclenchement de `pytest` sur chaque push et PR) pour tester automatiquement chaque brique future

### Jalon 1 — Cœur métier : Modèles cibles, Multi-entreprises & Catégories

* [ ]  **Définition du modèle central :** Création du modèle `Company` (Entreprise/Warehouse) pour valider l'architecture globale avec le mentor
* [ ]  **Modélisation du Catalogue :** Ajouter le modèle `Category` et amender `Product` pour intégrer la notion de catégories
* [ ]  **Modélisation de l'infrastructure :** Créer le modèle `Location` (nom, adresse, type dépôt/boutique) explicitement rattaché à une `Company`
* [ ]  **Modélisation des Flux :** Créer les modèles `Stock` (produit, lieu, quantité) et `Movement` (produit, lieu source/destination, quantité, date, raison)
* [ ]  **Périmètre Utilisateur :** Concevoir la table d'affectation `User ↔ Company` (avec gestion des droits par entreprise) pour valider le POC de sécurité
* [ ]  Générer les migrations, implémenter les méthodes `__str__` et configurer l'interface d'administration Django de base pour ces entités

### Jalon 2 — Périmètre, Sécurité & Filtrage

* [ ]  Mettre en place le filtrage systématique au niveau des requêtes (QuerySets personnalisés, Mixins de vues) : un utilisateur ne doit voir et modifier que les données des entreprises auxquelles il est rattaché
* [ ]  Implémenter les permissions par rôle (RBAC)
* [ ]  Écrire les premiers tests de périmètre et de cloisonnement inter-entreprises

### Jalon 3 — Catalogue complet & Authentification

* [ ]  Développer le CRUD complet pour les produits en utilisant les formulaires natifs Django avec gestion HTML/CSS "manuelle" (Contrôle total du rendu)
* [ ]  Intégrer l'import/export CSV du catalogue via `django-import-export`
* [ ]  Finaliser l'authentification : implémenter les fonctionnalités de `register` et de `password-reset` (nettoyage des `# TODO Temporaire` dans `src/urls.py`)

### Jalon 4 — Mouvements & Alertes transactionnelles

* [ ]  Créer la vue des mouvements de stock avec un formulaire dynamique (gestion des entrées, sorties et transferts)
* [ ]  Garantir la mise à jour transactionnelle sécurisée des quantités dans le modèle `Stock` lors d'un mouvement
* [ ]  Développer le système d'alertes de seuil critique (notifications in-app dès que `Stock.quantite < Product.seuil_alerte`)

### Jalon 5 — Tableau de bord & Optimisation BDD

* [ ]  Concevoir le tableau de bord principal avec intégration de Chart.js (graphiques des quantités par catégorie et évolution mensuelle)
* [ ]  Optimiser les requêtes MySQL en injectant systématiquement `select_related` et `prefetch_related` pour éliminer le risque de performance BDD (problème des requêtes N+1)

### Jalon 6 — Finitions & Livrables finaux

* [ ]  Personnaliser l'interface d'administration (filtres avancés, moteurs de recherche internes, affichages des colonnes d'audit)
* [ ]  Générer le jeu de données d'exemple attendu dans `fixtures/initial_data.json`
* [ ]  Étoffer la suite de tests unitaires et fonctionnels sous `pytest`
* [ ]  Finaliser la documentation du README (guide complet d'installation, commandes utiles, scénarios d'exemples)
