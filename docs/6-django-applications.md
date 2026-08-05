<div align="center">

<img src="../assets/img/logo.svg" alt="Logo Gestion de stocks" width="60" />

# Django Applications

Projet Gestion de stocks — document de travail

![Statut](https://img.shields.io/badge/Statut_du_document-En_cours_de_rédaction-purple.svg)  

<h3>

<a href="#access">Access</a> | <a href="#scope">Scope</a> | <a href="#core">Core</a> | <a href="#users">Users</a> | <a href="#company">Company</a> | <a href="#catalogue">Catalogue</a> | <a href="#inventory">Inventory</a> | <a href="#reporting">Reporting</a>

</h3>

</div>

Ce document détaille les rôles et composants de chaque application django.

---

## <a id="access">![](https://img.shields.io/badge/-App-darkblue.svg) Access

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

## <a id="scope">![](https://img.shields.io/badge/-App-darkblue.svg) Scope

Application qui rassemble le contexte d'entreprise courant, middleware et managers filtrants.

---

## <a id="core">![](https://img.shields.io/badge/-App-darkblue.svg)Core

Application qui rassemble le core de l'application web et les éléments partagés.

---

## <a id="users">![](https://img.shields.io/badge/-App-darkblue.svg) Users

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

## <a id="company">![](https://img.shields.io/badge/-App-darkblue.svg) Company

Gère les entreprises et leurs emplacements. Il s'agit du pivot central du multi-entreprises permettant de cloisonner le catalogue et l'inventaire de chaque organisation. 

L'application `Company `permet de répondre aux questions suivantes:

* Quelles entreprises existent ? 

* Où sont leurs lieux, entrepôts, boutiques, zones ?

---

## <a id="catalogue">![](https://img.shields.io/badge/-App-darkblue.svg)Catalogue

Application gérant le référentiel des produits.

Un produit peut se décliner en plusieurs variantes ayant chacun aucun à plusieurs attributs. La définition commune de ces variantes est le « modèle ». Le modèle peut avoir de zéro à plusieurs catégories. Modèles et variantes peuvent avoir des images associées. Le seuil d'inventaire bas est configuré par variant et par emplacement.

*Exemple: Un T-Shirt est le modèle, dans la catégorie Vêtement. Il se décline en 2 variantes de couleur: rouge et bleu. À la Boutique ABC, le seuil d'alerte bas est de 10 unités alors que dans l'Entrepôt X, il est de 50 unités.*

---

## <a id="inventory">![](https://img.shields.io/badge/-App-darkblue.svg)Inventory

Application gérant le suivi des stocks physiques, les unités de mesure et leur conversion ainsi que la traçabilité des flux de marchandises et les raisons des mouvements de stock.

---

## <a id="reporting">![](https://img.shields.io/badge/-App-darkblue.svg)Reporting

TODO