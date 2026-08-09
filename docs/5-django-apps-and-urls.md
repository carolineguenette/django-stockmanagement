<div align="center">

<img src="../assets/img/logo.svg" alt="Logo Gestion de stocks" width="60" />

# Applications django et Urls

Projet Gestion de stocks — docume nt de conception

![Statut](https://img.shields.io/badge/Statut_du_document-En_cours_de_rédaction-purple.svg)

<h3>
Partie I Apps : 
<a href="#core">Core</a> | <a href="#access">Access</a> | <a href="#scope">Scope</a> | <a href="#users">Users</a> | <a href="#company">Company</a> | <a href="#catalogue">Catalogue</a> | <a href="#inventory">Inventory</a> | <a href="#reporting">Reporting</a> | <a href="#others">Extensions</a>

</h3>

<h3>
Partie II Urls : 
<a href="#urls">Urls</a>

</h3>

</div>

Ce document détaille chaque application Django ainsi que le routage de base des urls.

[← Sécurité](4-data-security.md) | [Sommaire](2-conception.md) |  [Base de données →](6-database-models.md)

---

## ![](https://img.shields.io/badge/-App-darkblue.svg) Core <a id="core"></a>

Application qui rassemble le core de l'application web et les éléments partagés. Elle propose aussi des templates globaux.

<mark>TODO</mark> Plus d'infos (templates, etc)

---

## ![](https://img.shields.io/badge/-App-darkblue.svg) Access <a id="access"></a>

Application responsable du contrôle d'accès métier. Elle implémente un RBAC custom utilisé pour limiter les droits des employés par compagnie et par location selon les rôles / permissions.

L'application n'utilise donc pas les permissions natives `auth_permission` de Django pour les droits métier. Django `Auth `est conservé seulement pour l'identité, l'authentification, les sessions et l'administration technique.

À noter que le statut propriétaire n'est pas représenté par un rôle RBAC. Il est porté directement par le champ `is_owner` du modèle `User `custom. Par contre, certaines permissions de type owner sont définies dans le référentiel des permissions et peuvent donc être déléguées.

Les responsabilités de l'application `Access `sont:

1. accès des employés à une compagnie ;
2. accès des employés à une location ;
3. permissions métier ;
4. bypass owner ;
5. protection des vues globales owner.

#### Backend d'Authentification personnalisé

La méthode native de Django `has_perm()` est étandue par un `Backend d'authentification personnalisé`. Consulter le document sur la sécurité des données pour plus [détails ⬀](4-data-security.md#auth-backend). Dans le code, ça se traduit par l'utilisation de `has_perm()` pour vérifier les accès custom.

#### CompanyAccessService

<mark>TODO</mark> Déterminer si toujours nécessaire vs Backend d'auth perso

---

## ![](https://img.shields.io/badge/-App-darkblue.svg) Scope <a id="scope"></a>

Application qui rassemble le contexte d'entreprise courant, le middleware et les managers filtrants.

<mark>TODO</mark> Ajout infos et liens

---

## ![](https://img.shields.io/badge/-App-darkblue.svg) Users <a id="users"></a>

Application responsable de l'identité utilisateur et de l'infrastructure d'authentification.

Elle s'appuie sur Django Auth pour :

- l'authentification ;
- les sessions ;
- les mots de passe ;
- les champs standards comme `is_active`, `is_staff` et `is_superuser`.

Les permissions métier ne sont pas gérées par les tables natives `auth_group` ou `auth_permission`. Elles sont gérées dans l'application `access`. Voir les documents [data-security.md](data-security.md) pour plus de détails la mise en oeuvre des accès et [choices-and-analysis.md](3-choices-and-analysis.md) pour l'analyse et la présentation des options et des choix techniques réalisés.

<mark>TODO Suite à réviser et compléter</mark>

### OwnerService

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

---

## ![](https://img.shields.io/badge/-App-darkblue.svg) Company <a id="company"></a>

Application permettant de configurer les entreprises, leur unités de mesure et leurs emplacements (`locations`).

`Company` est le pivot central du multi-entreprises, permettant de cloisonner le catalogue et l'inventaire de chaque organisation.

Toutes les entreprises présentes en base appartiennent au même périmètre propriétaire. Ainsi, un utilisateur avec `users.User.is_owner=True` peut accéder à toutes les entreprises. Les employés n'ont accès qu'aux compagnies autorisées par le RBAC custom.

L'application `Company `permet de répondre aux questions suivantes:

* Quelles entreprises existent ?
* Comment sont configurés les lieux physiques et quels sont les types d'emplacements?
* Quelles sont les adresses postales des différents emplacements de l'entreprise?
* L'entreprise gère-t-elle la traduction des données dynamiques?
* Quels sont les unités de mesure utilisées par les produits du catalogue?

---

## ![](https://img.shields.io/badge/-App-darkblue.svg) Catalogue <a id="catalogue"></a>

Application gérant le référentiel des produits, leurs déclinaisons (variantes), leur classification (catégories), leurs images, leur conditionnement (packaging) et leurs caractéristiques techniques (seuil d'alerte bas). Chaque produit peut être configuré pour utiliser ou non les variants ou le conditionnement.

L'application `Catalogue` permet de répondre aux questions suivantes :

* Comment le produit est-il configuré (variants, conditionnement) ?
* Quels sont les produits de référence (modèles) et les articles finis (variantes) du catalogue ?
* Quels sont les visuels et images associés aux produits et aux catégories ?
* Comment les produits sont-ils classés (catégories hiérarchiques) ?
* Comment le produit est-il configuré pour la logistique ?
  * Alerte de seuil bas

La configuration des produits permet 4 situations:


| Id    | Variant | Packaging | Exemple Concret                                            |
| :---- | :-----: | :-------: | :--------------------------------------------------------- |
| **A** | **OFF** |  **OFF**  | **Un sac de chips** dans un dépanneur.                    |
| **B** | **OFF** |  **ON**  | **Des œufs** dans une épicerie.                          |
| **C** | **ON** |  **OFF**  | **Un t-shirt** dans une boutique de vêtements.            |
| **D** | **ON** |  **ON**  | **Des canettes de bière** dans une fabrique artisanale. |

### Impact pour l'UI/UX

#### A. UI simplifiée pour améliorer l'UX.

* Le modèle (`ProductModel`) et son (unique) produit physique (`Product`) sont gérés de manière transparente en une seule étape.
* Aucun attribut n'est configuré ( `AttributeKey`, `AttributeValue `et `ProductAttribute `ne contiennent aucune donnée sur ce produit).
* Le système crée un conditionnement (`Packaging`) unitaire "virtuel" : le module de packaging (*Packaging*) ne semble pas utilisé pour l'utilisateur.

*Exemple: Un T-Shirt est le modèle, dans la catégorie Vêtement. Il se décline en 2 variantes de couleur: rouge et bleu. Le conditionnement se fait toujours par unité, de manière transparente. À la Boutique ABC, le seuil d'alerte bas est de 10 unités alors que dans l'Entrepôt X, il est de 50 unités.*

#### B. UI hybride simple avec conditionnement

* Le modèle (`ProductModel`) et son (unique) produit physique (`Product`) sont gérés de manière transparente en une seule étape.
* Aucun attribut n'est configuré ( `AttributeKey`, `AttributeValue `et `ProductAttribute `ne contiennent aucune donnée sur ce produit).
* L'utilisateur peut créer ses conditionnements (`Packaging`).

*Exemple: "Oeuf Barnaby Bio" est créé. La vente propose "Douzaine" (12 x l'unité de base) et "Caissette de 30 oeufs" (30 X l'unité de base). Ces oeufs sont achetés par "Boîte de 12 douzaines" (144 oeufs) et "Boîte de 5 caissettes" (150 oeufs). Le stock en inventaire permet de suivre chacun de ces conditionnements, leur quantité en inventaire et déclenche une alerte de seuil bas selon leur location.

#### C. UI avec variants sans conditionnement

* Le modèle (`ProductModel`) est créé.
* Les variants (`Product`) sont créés.
* Les attributs et leur valeur sont créés et/ou associés avec le produit ( `AttributeKey`, `AttributeValue `et `ProductAttribute `)
* Le système crée un conditionnement (`Packaging`) unitaire "virtuel" : le module de packaging (*Packaging*) ne semble pas utilisé pour l'utilisateur.

*Exemple: Le "T-Shirt en coton" est le modèle, dans la catégorie Vêtement. Il se décline en 2 variantes de couleur: rouge et bleu et 3 variantes de taille: S, M et L. Le conditionnement se fait toujours par unité, de manière transparente. À la Boutique ABC, le seuil d'alerte bas est de 10 unités alors que dans l'Entrepôt X, il est de 50 unités.*

#### D. UI complet avec variants et conditionnement

* Le modèle (`ProductModel`) est créé.
* Les variants (`Product`) sont créés.
* Les attributs et leur valeur sont créés et/ou associés avec le produit ( `AttributeKey`, `AttributeValue `et `ProductAttribute `)
* L'utilisateur peut créer ses conditionnements (`Packaging`).

*Exemple: Le produit "Bière artisanale" est le modèle. Il se décline en 2 variantes de saveur: IPA et Blonde. Le conditionnement de IPA se fait à l'unité (canette), en pack de 6 ou en carton de 12.*

---

## ![](https://img.shields.io/badge/-App-darkblue.svg)Inventory <a id="inventory"></a>

Application gérant l'état des stocks physiques, la traçabilité des lots et l'historique complet des mouvements de marchandises.

L'application `Inventory` traduit les données théoriques de l'application Catalogue en volumes réels et localisés au sein des emplacements définis par Company. Elle sert de pivot pour toutes les opérations logistiques (réception, stockage, expédition).

L'application `Inventory` permet de répondre aux questions suivantes :

* Où se trouvent les produits ?
* En quelles quantités un produit se décline, incluant la quantité de chaque variante ou conditionnement ?
* Quelle est l'histoire de la vie d'un produit en stock ?
* Quelle est la raison de chacun des mouvements de stock réalisé ?

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

Les **vues globales** sont séparées et explicitement réservées aux propriétaires et aux utilisateurs avec les permissions appropriées :

```text
/g/...
```


| Contexte         | Comportement                                         |
| :--------------- | :--------------------------------------------------- |
| /c/company-a/.,, | filtre sur company-a                                 |
| /g/...           | requêtes globales explicites                        |
| aucun contexte   | Erreur / Refus sur les modèles company-scoped       |
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
