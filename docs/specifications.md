# Gestion de stocks — Projet Portfolio

<img src="https://img.shields.io/badge/Statut_du_document-Final-purple.svg" alt="Statut" />

## Contexte et vision

Dans le cadre de ce projet, vous serez amenés à réaliser une application web complète de gestion de stocks. Le commanditaire souhaite disposer d'une application moderne et professionnelle permettant de gérer l'inventaire de plusieurs entreprises. L'accent est mis sur la qualité du code, la sécurité et l'expérience utilisateur. Le projet doit également intégrer GitHub Actions pour l'intégration continue, préparant ainsi les étudiants aux exigences du monde professionnel.

## Objectifs pédagogiques

* **Approfondir la maîtrise de Django** : modèles, vues génériques, templates, signaux et système d'authentification.
* **Concevoir une architecture modulaire et évolutive** : séparation par applications (catalogue, entrepôt, reporting, utilisateurs).
* **Mettre l'accent sur la sécurité et les bonnes pratiques Web** : système d'authentification, permissions, CSRF, etc.
* **Introduire les fondements DevOps** : tests d'intégration dans un pipeline GitHub Actions.

## Fonctionnalités attendues

1. **Gestion des utilisateurs et rôles**
   Inscription, authentification, réinitialisation de mot de passe.
2. **Catalogue produits**
   CRUD complet, import/export CSV.
3. **Multi-entreprises**
   Possibilité de gérer les stocks de plusieurs entreprises, chaque utilisateur étant limité à son périmètre (on peut affecter un utilisateur à une ou plusieurs entreprises).
4. **Multi-langues et internationalisation (i18n) – AJOUT PERSO**
   Possibilité de traduire l’application (anglais et français pour le moment). Chaque utilisateur peut afficher l’application selon ses préférences à ce niveau.
5. **Mouvements de stock**
   Entrées, sorties, historisation avec horodatage.
6. **Alertes seuil critique**
   Notification dans l'application lorsque la quantité passe sous le seuil défini et possibilité pour chaque produit de définir le seuil d'alerte.
7. **Tableau de bord & statistiques**
   Graphiques simples (quantités par catégorie, évolution mensuelle) rendus avec Chart.js.
8. **Administration personnalisée**
   Interface admin (affichage, filtres, recherche) permettant la gestion des utilisateurs, produits, stocks, etc.

## Scénario d'usage principal

> En tant que propriétaire de plusieurs entreprises, je veux pouvoir gérer les stocks de mes différentes entreprises depuis une seule interface, afin de suivre facilement les niveaux d'inventaire et d'être alerté quand les produits atteignent un seuil critique.

### Exemple concret d'utilisation

* Le propriétaire dispose d'un compte administrateur et peut créer des entreprises, des produits, des stocks et des utilisateurs.
* Chaque compte utilisateur dispose de droits spécifiques pour chaque entreprise.
* Un utilisateur peut créer, modifier et supprimer des produits et modifier les stocks.
* Le propriétaire a une vision d'ensemble de ses entreprises et de ses stocks sur un tableau de bord.
* Le propriétaire peut voir les alertes de seuil critique pour chaque entreprise.

## Spécifications techniques

### Architecture

* Application Django classique avec base de données.
* Langage : Python 3.11 minimum et Django 5.x.
* Dépendances tierces conseillées : `pytest-django`, `django-import-export`, `django-cleanup`, `django-crispy-forms`, `django-environ`.

### Modèles

* **Product** : SKU, nom, description, prix, seuil d'alerte.
* **Location** : nom, adresse, type (dépôt/boutique).
* **Stock** : produit, lieu, quantité.
* **Movement** : produit, lieu source/destination, quantité, date, raison.

### Vues

* Vue spéciale pour les mouvements avec formulaire dynamique.
* Dashboard avec graphiques Chart.js.

### Tests

* Tests unitaires.
* Tests fonctionnels.
* Fixtures pour données de test.

## Livrables attendus

Dépôt GitHub public contenant :

* Code source complet et commenté.
* Jeux de données d'exemple (`fixtures/initial_data.json`).
* Scripts ou instructions de lancement.
* Documentation utilisateur dans le `README.md` (installation, commandes, exemples).

Jeu de tests automatisés :

* `pytest` exécutés par un workflow GitHub Actions.

## Gestion des risques


| Risque                                          | Mesure préventive                                                                              |
| :---------------------------------------------- | :---------------------------------------------------------------------------------------------- |
| **Complexité de la gestion multi-entreprises** | Commencer par un POC simple, valider l'architecture des modèles avec le mentor dès le début. |
| **Problèmes de performance BDD**               | Optimiser les requêtes, utiliser`select_related`/`prefetch_related`.                           |
| **Difficultés avec GitHub Actions**            | Partir de templates, commencer avec des tests basiques.                                         |
