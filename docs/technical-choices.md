![Statut](https://img.shields.io/badge/Statut_du_document-OLD_Conserver_pour_revision_avant_suppression-purple.svg)

## Conception & choix techniques

## 🧱 Architecture des applications Django

Le projet est découpé de manière modulaire en applications Django distinctes afin de garantir une séparation des responsabilités :

* **`main` Application principale :** Gère le cœur de l'infrastructure, la page d'accueil générale, la structure globale de l'interface utilisateur (layout global du tableau de bord) et les vues d'erreurs génériques. Les scripts d'importation et d'exportation de données CSV font aussi partie de main.
* **`users` (Gestion des Comptes) :** Centralise le modèle utilisateur personnalisé, la table de liaison des permissions (`Membership`), ainsi que l'ensemble du cycle d'authentification (connexion, inscription, réinitialisation de mot de passe).
* **`companies` (Infrastructure Logistique) :** Gère les entités structurelles du réseau d'inventaire, spécifiquement les modèles `Company` (Entreprises) et `Location` (Sites, dépôts et boutiques).
* **`catalogue` (Gestion des Articles) :** Contrôle les fiches produits (`Product`), l'arborescence des catégories (`Category`), les visuels associés (`ProductImage`)
* **`inventory` (Gestion des quantités de produit) :** Gère l'inventaire et tout ce qui concerne les mouvements de quantité
* **`reporting` (Tableau de bord, indicateurs & décisions) :** Dédiée au calcul des indicateurs de performance, au suivi des alertes automatiques de seuils critiques et à l'agrégation des métriques pour les graphiques interactifs (Chart.js).

### 👤 Utilisateurs

* **Modèle Utilisateur Personnalisé :** Extension d'`AbstractUser` pour intégrer dynamiquement le choix de la langue et des préférences régionales par profil.
* **Authentification Django :** Utilisation des vues d'authentification natives de Django pour la connexion, la déconnexion et la réinitialisation de mot de passe, associées à des templates personnalisés.

### 🛡️ Sécurité, périmètre et rôles

* **Contrôle d'Accès Granulaire (RBAC) :** Gestion des permissions par « atomes » combinés en rôles modifiables (Spécifications complètes dans la [Documentation de l'architecture des rôles](./docs/architecture-roles.md)).
* **Cloisonnement Strict :** Filtrage systématique des requêtes (QuerySets) au niveau des vues et des API pour garantir qu'un utilisateur connecté ne puisse voir et modifier que les données auxquelles il a droit.

### 📦 Catalogue Produits

* **Modélisation & Audit :** Modèle `Product` incluant un index SKU unique, validation stricte des prix (≥ 0) et horodatage d'audit complet  (`created_at`, `updated_at`, `created_by`, `updated_by`).
* **Gestion du Stockage Médias :** Modèle `ProductImage` prenant en charge le renommage automatisé des fichiers physiques (SKU + UUID) et couplé à un système de nettoyage des fichiers d'images orphelins sur le stockage.
* **Persistance & Échanges :** Formulaires natifs et contrôleurs de gestion (CRUD) du catalogue, intégrés avec un module d'importation et d'exportation de masse au format CSV.

### 📉 Logique d'Inventaire & Reporting BDD

* **Modélisation Métier :** Traduction relationnelle des flux logistiques à travers deux entités clés complémentaires : `Stock` (quantités physiques d'un produit localisées dans un site de `warehouse`) et `Movement` (historisation globale et immuable des flux de marchandises).
* **Déclencheurs d'Alertes :** Logique métier transactionnelle évaluant les stocks lors de chaque mouvement pour pousser une alerte interne dès que la quantité physique franchit le seuil critique défini sur la fiche produit.
* **Optimisation des Requêtes BDD :** Utilisation systématique des méthodes `select_related` et `prefetch_related` sur l'ORM Django afin d'éliminer les risques de régression de performance (requêtes N+1) lors du chargement des statistiques MySQL pour Chart.js.

### 🌍 Internationalisation (i18n) & Localisation

* **Routage par Langue :** Prise en charge transparente du français, de l'anglais et de l'espagnol via l'activation de `LocaleMiddleware`routage par `i18n_patterns`.
* **Adaptation Régionale :** Exploitation du moteur de régionalisation natif de Django pour automatiser l'affichage localisé des formats de dates, des heures et de la devise au niveau global de l'application.

### 🎨 Expérience Utilisateur (UX/UI)

* **Interface Responsive :** Grille graphique fluide et adaptative assurant une accessibilité et un rendu impeccables sur ordinateurs, tablettes et terminaux mobiles.
* **Thèmes Visuels :** Intégration complète des modes clair et sombre (Light/Dark mode) pour réduire la fatigue visuelle des opérateurs selon leur environnement de travail.
* **Navigation Métier :** Menus de navigation simplifiés et formulaires à entrée rapide, calibrés pour la gestion de terrain.
* **Simulation de Scan :** Module d'interface simulant l'utilisation de scan de codes-barres (carte d'ID pour l'authentification, code de produits) pour accélérer et fiabiliser la saisie des entrées, sorties et transferts d'inventaire.
