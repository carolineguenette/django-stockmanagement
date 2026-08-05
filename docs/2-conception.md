<div align="center">

<img src="../assets/img/logo.svg" alt="Logo Gestion de stocks" width="60" />

# Conception

Projet Gestion de stocks — document de travail

</div>

Ce fichier documente les assertions et choix architecturaux du projet.

---

## Introduction

Ce projet est une application de gestion d'inventaire multi-entreprises appartenant à un même propriétaire. Toutes les entreprises créées en base de données sont donc reliées par cette propriété commune.

*Ce que ce n'est pas* :  Ce projet n'est pas une application SaaS multi-tenants où plusieurs organisations indépendantes cohabitent sans se connaître.

## Utilisateurs

Les utilisateurs sont le propriétaire et tous ses employés. 

Les accès des employés sont limités par un RBAC (Role-Based Acces Control) personnalisé.

| Utilisateurs          | Accès                    | User DB Field                                               |
| --------------------- | ------------------------ | ----------------------------------------------------------- |
| Propriétaire          | Tous les accès Front-end | `is_owner=True`,`is_superuser=False`,`is_staff=False`,      |
| Employés              | Accès limité par RBAC    | `is_owner=False`,`is_superuser=False`,`is_staff=False`,     |
| Administrateur Django | Tous les accès           | `is_owner=PEU IMPORTE`,`is_superuser=True`,`is_staff=True`, |

L'application peut avoir plusieurs propriétaires. 

* Seul un propriétaire peut promouvoir un utilisateur propriétaire.

* L'application doit toujours avoir au minimum un propriétaire actif (le dernier propriétaire ne peut pas se révoquer ou se désactiver lui-même)

L'administration Django est réservée exclusivement pour la technique (<mark>TODO: reformuler</mark>)

#### Distinction entre *propriétaire* et *super-utilisateur*

* Être propriétaire est un rôle métier. Cette personne peut :
  
  * voir toutes les compagnies ;
  
  * gérer les employés ;
  
  * gérer les rôles ;
  
  * consulter les rapports consolidés ;
  
  * effectuer des mouvements inter-company si prévu ;
  
  * voir les données financières globales ;
  
  * gérer les paramètres métier.

* Être un super-utilisateur est un rôle technique Django. Cette personne peut : 
  
  * accéder à Django Admin ;
  
  * réaliser l'administration technique ;
  
  * corriger les données ;
  
  * effectuer la maintenance ;
  
  * effectuer les migrations.

Le super-utilisateur doit faire particulièrement attention pour ne pas introduire de croisements inter-entreprises (*par exemple: assigner un produit de l'entreprise A à une location de l'entreprise B*). Grâce aux barrières de sécurité (voir plus bas), le propriétaire sera techniquement empêché de faire ce genre de manipulation erronée.

## Accès et permissions

Le modèle de sécurité doit isoler les données par entreprise  (`company`) pour qu'un employé n'ait accès qu'aux compagnies et locations autorisées.

### Réflexion sur le système *auth* natif de Django

#### Authentification

Le projet utilise toute la partie authentification de auth. (login, session, cookie, etc)

#### Accès et permissions

Le système de permission de django n'est pas adapté aux besoins du projet. Il ne peut pas isoler par compagnie  et ne permet pas d'avoir des permissions fines (*ex: augmenter la quantité d'un produit en inventaire en faisant un achat, déclarer une perte d'inventaire en raison d'un bris*).

##### RBAC

Le propriétaire bypass le RBAC

```python
if user.is_owner:
    return True
```

C'est simple et ça évite d'avoir à assigner tous les rôles au propriétaire. Par contre, il faut auditer les actions *owner*.

## Barrieres de sécurité

La sécurité des données ne peut pas reposer uniquement sur la logique métier. Ainsi, 2 barrières, ayant chacune leur rôle, seront implémentées.

#### CompanyMiddleware

Son rôle est de définir le contexte d'entreprise à partir de l'URL demandée. AInsi, si une page *company score* est demandée (`url: .../c/<company_slug>`), il va :

1. charger la compagnie active ;

2. si user est inactif : refuser l'accès ;

3. si user est owner : autoriser ;

4. sinon vérifier RBAC ;

5. définir request.company

#### CompanyManager

Son rôle est de filtrer les données selon l'entreprise active. <mark>TODO Compléter</mark>

**Attention**: si la page est company-scope (`.../c/company-a/...`), alors on tri selon l'entreprise, même si l'utilisateur est le propriétaire. Ainsi, on limite les erreurs dûes à une requête oubliée.

### Cas des vues globales

#### Vues d'authentification

```
.../login
.../register
.../password-lost
```

Ces vues doivent évidemment rester accessibles sans contexte.

#### Vues propriétaire

```
.../g/dashboard/
.../g/inventory/
.../g/reports/
```

Ces vues ne doivent pas utiliser le même contexte par entreprise car elles *doivent* récupérer l'information de plusieurs entreprises. Elles ont besoin d'un contexte explicite (ou un manager non filtré?)

<mark>TODO: url "owner" ou autre terme?</mark>

## Évolutions pssibles

* Vers un SaaS complet
  
  * Ajout d'un modèle `Account `et lien vers les modèles `User `et `Company`.
  
  * Complexité accrue. Sécurité multi-tenant particulièrement sensible.