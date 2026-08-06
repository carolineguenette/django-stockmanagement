<div align="center">

<img src="../assets/img/logo.svg" alt="Logo Gestion de stocks" width="60" />

# Conception — Sommaire

Projet Gestion de stocks — document de travail

![Statut](https://img.shields.io/badge/Statut_du_document-En_cours_de_rédaction-purple.svg)

<h3>

[Introduction](#introduction) | [Utilisateurs](#users) | [Authentification et permissions](#auth) | [Barrières de sécurité](#barrieres-de-sécurite) 

</h3>

</div>

Ce fichier présente un sommaire du projet, présente les éléments de base et agit comme table des matières globale des documents de conception.

[← Spécifications](1-specifications.md) | [README](../README.md) |  [Analyse →](3-choices-and-analysis.md)

Table des matières globale des documents de conception :

1. [Cahier des charges](1-specifications.md)
2. Conception (*ce document*)
3. [Analyse technique et choix](3-choices-and-analysis.md)
4. [Règles de sécurité et logique algorithmique du RBAC](4-data-security.md)
5. [Découpage modulaire du code (django apps et urls)](5-django-app-and-urls.md)
6. [Database (Schéma et django-models)](6-database-models.md)
7. [Arborescence des fichiers](7-project-structure.md)
8. [Gestion de projet, Jira et GitHub Actions](8-dev-plan.md)

---

## Introduction

Ce projet est une application de gestion d'inventaire multi-entreprises appartenant à un même propriétaire. Toutes les entreprises créées en base de données sont donc reliées par cette propriété commune.

*Ce que ce n'est pas* :  Ce projet n'est pas conçu, dans sa version actuelle, comme une plateforme SaaS multi-clients où plusieurs organisations indépendantes cohabitent dans la même base de données.

### Conséquences :

- un utilisateur propriétaire (`is_owner=True`) a accès à toutes les entreprises présentes en base ;
- les employés (`is_owner=False`) ont des accès limités par un RBAC personnalisé ;
- les données restent rattachées à une compagnie afin de permettre le filtrage, les rapports, les permissions et l'intégrité métier ;
- les vues *company-scoped* (url `/c/company-slug/...`) et les *vues globales owner* (url `/g/...`) sont explicitement séparées ;
  - un propriétaire consultant une url `/c/company-slug/...` aura aussi une vue limitée à l'entreprise active.

## Utilisateurs <a id="users"></a>

### Types d'utilisateurs


| Rôle / Type              | Drapeaux (Flags)                                                           | Périmètre et Accès                                                                                     |
| :------------------------ | :------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------- |
| **Propriétaire métier** | `is_owner=True`<br>`is_superuser=False`<br>`is_staff=False`                | Accès métier total à toutes les compagnies, aux vues globales et aux paramètres de l'entreprise.      |
| **Employé**              | `is_owner=False`<br>`is_superuser=False`<br>`is_staff=False` + RBAC custom | Accès limité par compagnie, emplacement (`location`) et permissions spécifiques du RBAC personnalisé. |
| **Administrateur Django** | `is_owner=False`<br>`is_superuser=False`<br>`is_staff=True`                | Accès exclusif à l'interface d'administration technique de Django.                                      |
| **Superuser technique**   | `is_owner=Indifférent`<br>`is_superuser=True`<br>`is_staff=True`          | Accès technique total au système (distinct du propriétaire métier).                                   |

### Distinction des rôles : Métier vs Technique

#### Rôle Métier : Le Propriétaire (`is_owner`)

* **Définition** : Rôle purement fonctionnel et commercial (ne remplace pas les privilèges techniques Django).
* **Capacités** :
  * Voir toutes les compagnies et les données financières globales.
  * Consulter les rapports consolidés et gérer les paramètres métier.
  * Effectuer des mouvements inter-company (protégés par des barrières de sécurité logicielles pour éviter les erreurs de croisement de données).
  * Gérer les employés et leurs rôles.

#### Rôle Technique : Le Super-utilisateur / Staff (`is_superuser` / `is_staff`)

* **Définition** : Rôle technique réservé à la maintenance et aux opérations système de Django.
* **Capacités** : Accéder à l'admin Django, réaliser la maintenance, corriger les données et exécuter les migrations.
* **Avertissement** : Attention à ne pas créer de croisements accidentels de données entre entreprises (ex. lier un produit A à une location B).

### Règles de gestion et contraintes

#### Gestion des Propriétaires

* L'application peut compter plusieurs propriétaires.
* Seul un propriétaire peut promouvoir un autre utilisateur au rang de propriétaire.
* **Sécurité** : L'application doit conserver au minimum un propriétaire actif. Le dernier propriétaire ne peut pas se révoquer ou se désactiver lui-même.

#### Gestion des Employés

* Les employés sont des utilisateurs globaux restreints par le RBAC personnalisé.
* Un employé peut intervenir sur une ou plusieurs entreprises avec des rôles distincts.
* Un employé habilité peut créer d'autres employés et leur assigner des rôles, mais **il ne peut jamais modifier** la propriété `is_owner` ni dépasser son propre périmètre de responsabilités.

---

## Authentification et permissions <a id="auth"></a>

Le modèle de sécurité doit isoler les données par entreprise  (`company`) pour qu'un employé n'ait accès qu'aux compagnies et locations autorisées.

### Authentification

Le projet utilise toute la partie authentification de auth. (login, session, cookie, etc)

### Gestion des accès

Le système de permission de django n'est pas adapté aux besoins du projet. Il ne peut pas isoler par compagnie et ne permet pas d'avoir des permissions fines (*ex: augmenter la quantité d'un produit en inventaire en faisant un achat, déclarer une perte d'inventaire en raison d'un bris*). Un RBAC personnalisé sera donc mis en place.

---

## Barrières de sécurité

La sécurité des données ne peut pas reposer uniquement sur la logique métier. Ainsi, 2 barrières, ayant chacune leur rôle, seront implémentées: `CompanyMiddleware` et `CompanyScopedManager`.