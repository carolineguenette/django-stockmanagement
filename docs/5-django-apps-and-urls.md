<div align="center">

<img src="../assets/img/logo.svg" alt="Logo Gestion de stocks" width="60" />

# Modules et séparation du code - Django Apps et Urls

Projet Gestion de stocks — document de conception

![Statut](https://img.shields.io/badge/Statut_du_document-En_cours_de_rédaction-purple.svg)  

<h3>
Partie I Apps : 
<a href="#access">Access</a> | <a href="#scope">Scope</a> | <a href="#core">Core</a> | <a href="#users">Users</a> | <a href="#company">Company</a> | <a href="#catalogue">Catalogue</a> | <a href="#inventory">Inventory</a> | <a href="#reporting">Reporting</a>

</h3>

<h3>
Partie II Urls : 
<a href="#urls">Urls</a>

</h3>

</div>

Ce document détaille la division du code en applications django ainsi que le routage des urls.

[← Sécurité](4-data-security.md) | [Sommaire](2-conception.md) |  [Base de données →](6-database-models.md)

---

## ![](https://img.shields.io/badge/-App-darkblue.svg) Access <a id="access"></a>

Application qui gère les accès utilisateurs et permet de définir les rôles. 

En particulier :

1. accès des employés à une compagnie ;

2. accès des employés à une location ;

3. permissions métier ;

4. bypass owner ;

5. protection des vues globales owner.

#### CompanyAccessService

```p
user.is_owner => True
sinon user a au moins un rôle actif dans company
```

#### PermissionService

```
user.is_owner => True pour permissions métier
sinon vérifier RolePermission/UserRole
```

Le bypass owner concerne exclusivement les permissions métier, pas les droits techniques Django (pas d'accès au paneau administratif de django)

---

## ![](https://img.shields.io/badge/-App-darkblue.svg) Scope <a id="scope"></a>

Application qui rassemble le contexte d'entreprise courant, middleware et managers filtrants.

---

## ![](https://img.shields.io/badge/-App-darkblue.svg)Core <a id="core"></a>

Application qui rassemble le core de l'application web et les éléments partagés.

---

## ![](https://img.shields.io/badge/-App-darkblue.svg) Users <a id="users"></a>

Gère les utilisateurs et leur permission. [Voir le document data-security.md](data-security.md) pour plus de détails sur la mise en oeuvre des accès et les choix techniques réalisés à ce niveau.

### Users Services

```text
src/users/services/owner_service.py
```

Responsabilités :

* créer un owner ;

* promouvoir un utilisateur en owner ;

* retirer le statut owner ;

* désactiver un owner ;

* vérifier qu’il reste au moins un owner actif ;

* empêcher qu’un non-owner crée un owner.

Le service peut appeler access.PermissionService pour vérifier certaines permissions employé si nécessaire.

---

## ![](https://img.shields.io/badge/-App-darkblue.svg) Company <a id="company"></a>

Gère les entreprises et leurs emplacements. Il s'agit du pivot central du multi-entreprises permettant de cloisonner le catalogue et l'inventaire de chaque organisation. 

L'application `Company `permet de répondre aux questions suivantes:

* Quelles entreprises existent ? 

* Où sont leurs lieux, entrepôts, boutiques, zones ?

---

## ![](https://img.shields.io/badge/-App-darkblue.svg)Catalogue <a id="catalogue"></a> 

Application gérant le référentiel des produits.

Un produit peut se décliner en plusieurs variantes ayant chacun aucun à plusieurs attributs. La définition commune de ces variantes est le « modèle ». Le modèle peut avoir de zéro à plusieurs catégories. Modèles et variantes peuvent avoir des images associées. Le seuil d'inventaire bas est configuré par variant et par emplacement.

*Exemple: Un T-Shirt est le modèle, dans la catégorie Vêtement. Il se décline en 2 variantes de couleur: rouge et bleu. À la Boutique ABC, le seuil d'alerte bas est de 10 unités alors que dans l'Entrepôt X, il est de 50 unités.*

---

## ![](https://img.shields.io/badge/-App-darkblue.svg)Inventory <a id="inventory"></a>

Application gérant le suivi des stocks physiques, les unités de mesure et leur conversion ainsi que la traçabilité des flux de marchandises et les raisons des mouvements de stock.

---

## ![](https://img.shields.io/badge/-App-darkblue.svg)Reporting <a id="reporting"></a>

TODO



---



### URLs company-scoped et vues globales owner <a id="urls"></a>

Les **vues métier liées à une compagnie** utilisent le format suivant :

```text
/c/<company_slug>/...
```

Ces vues sont toujours filtrées sur la compagnie courante, y compris lorsque l'utilisateur est le propriétaire.

Les **vues globales** sont séparées et explicitement réservées aux propriétaires :

```text
/g/...
```


| Contexte         | Comportement                                     |
|:---------------- |:------------------------------------------------ |
| /c/company-a/.,, | filtre sur company-a                             |
| /global/...      | requêtes globales explicites                     |
| aucun contexte   | Erreur / Refus sur les modèles company-scoped    |
| Django-admin     | Accès via manager spécial ou all_objects réservé |


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

## Évolutions pssibles

* Vers un SaaS complet

  * Ajout d'un modèle `Account `et lien vers les modèles `User `et `Company`.
  * Complexité accrue. Sécurité multi-tenant particulièrement sensible.

---
---
---

  
Table des matières

1. [RBAC personnalisé](#rbac) 
2. <a href="#midleware">CompanyMiddleware</a>
3. <a href="#manager">CompanyScopedManager</a>
4. <a href="#permissions">Référentiel des permissions</a> 
5. <a href="#roles">Roles par défaut</a> 
6. <a href="#tests">Tests de sécurité</a>

---