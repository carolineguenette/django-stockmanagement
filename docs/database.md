<div align="center">

<img src="../assets/img/logo.svg" alt="Logo Gestion de stocks" width="60" />

# Database (modèles et apps django)

Projet Gestion de stocks — document de travail

![Statut](https://img.shields.io/badge/Statut_du_document-V1_Prêt_pour_POC-purple.svg)  [![Schema](https://img.shields.io/badge/Schema_DB-LucidChart-F45D22.svg)](https://lucid.app/lucidchart/786327e6-745d-4881-95e1-39f3fdf33c66/edit?viewport_loc=4219%2C-3440%2C2860%2C1419%2C0_0&invitationId=inv_16c572fc-aaf2-4b0e-9e8f-636d2cf04698)

<h3>

<a href="#auth">Auth</a> (Natif Django) |
<a href="#core">Core</a> |
<a href="#users">Users</a> |
<a href="#company">Company</a> |
<a href="#catalogue">Catalogue</a> |
<a href="#inventory">Inventory</a> |
<a href="#reporting">Reporting</a> |
<a href="#others">Autres...</a>

</h3>

</div>

Ce document ajoute des commentaires explicatifs sur le schéma de la base de données (choix technique, notes de développement, etc.). Les apps django, modèles, table ou noms des champs ne sont pas listés de manière exhaustives dans le présent document (se référer au schéma).

[![](database_lucidchart.png)](database_lucidchart.png)
[Voir le Schéma de la base de données sur LucidChart](https://lucid.app/lucidchart/786327e6-745d-4881-95e1-39f3fdf33c66/edit?viewport_loc=4219%2C-3440%2C2860%2C1419%2C0_0&invitationId=inv_16c572fc-aaf2-4b0e-9e8f-636d2cf04698) - compte gratuit LucidChart requis.

---

## <a id="auth"> ![](https://img.shields.io/badge/-App-darkblue.svg) Auth

Application native du système d'authentification de Django qui stocke les groupes d'utilisateurs et les permissions pour gérer les autorisations.

### ![](https://img.shields.io/badge/-Model-blue.svg) Group (table `auth_group`)

Cette table stocke les groupes de permissions pour gérer les autorisations en lot.

Pour contourner la limitation de django qui n'a pas de système du type "AbstractGroup" qui permettrait d'ajouter un champs company_id, le champs `name `sera préfixé par "company_id_" (*Exemple: 1_Gestionnaire*). Cette gestion sera totalement transparente pour l'utilisateur final. Voir [docs/database.md](./docs/database.md#isolation_rôles) pour plus de détails.

---

## <a id="core"> ![](https://img.shields.io/badge/-App-darkblue.svg) Core

Application qui rassemble le core de l'application web.

### ![](https://img.shields.io/badge/-Model-blue.svg) Settings (table `core_settings`)

Cette table centralise les configurations globales .


| ![](https://img.shields.io/badge/-Field-turquoise.svg) | Note                                                                                                                                                                                                                                                            |
| ------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| badge_code                                             | ![](https://img.shields.io/badge/DEV-VX-green.svg) Permet de se connecter en scannant un code bar sur un badge d'identification                                                                                                                                |
| currency                                               | ![](https://img.shields.io/badge/DEV-VX-green.svg) Sert de référence monétaire globale pour l'ensemble de l'application et donc toutes les compagnies et leurs locations.<br />Est écrasé par Company.currency et Location.currency s'ils sont définis  |

## <a id="users"> ![](https://img.shields.io/badge/-App-darkblue.svg) Users

Gère les utilisateurs et leur permission. [Voir le document data-security.md](data-security.md) pour plus de détails sur la mise en oeuvre des accès et les choix technique réalisés à ce niveau.

### ![](https://img.shields.io/badge/-Model-blue.svg) User (table `users_user`)

Entité centrale des utilisateurs étandant le modèle de base de Django (`AbstractUser`).

### ![](https://img.shields.io/badge/-Model-blue.svg) Role (table `users_role`)

Table de liaison tripartite entre `users_user `et `auth_group`. Elle sert à assigner un ou plusieurs rôles à un utilisateur donné. Remplace le modèle par défaut de Django pour l'attribution des permissions, qui n'avait aucun moyen d'isoler les données de chaque entreprise (company). Une quatrième clé optionnelle (location_id) permet d'affiner encore plus le niveau d'accès.

![](https://img.shields.io/badge/Unique-user__id_company__id_role__id_location__id-blueviolet.svg)


| ![](https://img.shields.io/badge/-Field-turquoise.svg) | Note                                                                                                    |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| location_id                                            | Si NULL, le rôle s'applique à TOUTE la compagnie. Sinon, uniquement à ce lieu et ses sous-locations. |

### ![](https://img.shields.io/badge/-Model-blue.svg) Permissions (table `users_permissions`)

Table de liaison tripartite entre `users_user `et `auth_permission`. Elle sert à assigner directement une permission à un utilisateur, sans passer par les rôles, tout en respectant le principe d'isolation des compagnies.

![](https://img.shields.io/badge/Unique-user__id_company__id_role__id_location__id-blueviolet.svg)


| ![](https://img.shields.io/badge/-Field-turquoise.svg) | Note                                                                                                    |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| location_id                                            | Si NULL, le rôle s'applique à TOUTE la compagnie. Sinon, uniquement à ce lieu et ses sous-locations. |

---

# <a id="company"> ![](https://img.shields.io/badge/-App-darkblue.svg) Company

Gère les entreprises et leurs locations. Il s'agit du pivot central du multi-tenant permettant de cloisonner hermétiquement le catalogue et les stocks de chaque organisation.

### ![](https://img.shields.io/badge/-Model-blue.svg) Company (table `company_company`)

Liste des entreprises gérées. Chaque compagnie est indépendante et isolée des autres. Seul les super-user peuvent voir les informations globales de toutes les compagnies.


| ![](https://img.shields.io/badge/-Field-turquoise.svg) | Note                                                                                                                                                                                                                             |
| ------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| currency                                               | ![](https://img.shields.io/badge/DEV-VX-green.svg) Sert de référence monétaire pour cette compagnie. <br />Écrase le paramètre global de Settings et peut être écrasé par le paramètre défini dans Location.currency |

### ![](https://img.shields.io/badge/-Model-blue.svg) Location (table `company_location`)

Table modélisant la hiérarchie complète de l'entreprise.

*Exemples:*

- une entreprise peut être composée d'une boutique A à l'adresse x et d'un entrepôt B à l'adresse y.
- la boutique A peut localiser son stock en créant une Zone emballage, Zone Frigo, Étagère A1, etc.


| ![](https://img.shields.io/badge/-Field-turquoise.svg) | Note                                                                                                                                                                                                             |
| :----------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| strret_address<br />city<br />country<br />postal_code | Choix fait de séparer l'adresse sur plusieurs choix pour faciliter la recherche/filtrage, uniformiser les données et permettre l'extension (ex: API tiers de livraison)                                        |
| currency                                               | ![](https://img.shields.io/badge/DEV-VX-green.svg) Sert de référence monétaire pour cette location. <br />Écrase les paramètres plus globaux (Settings, Company)                                         |
| parent_id                                              | ![](https://img.shields.io/badge/DEV-V1-green.svg) Toujours NULL<br />![](https://img.shields.io/badge/DEV-VX-green.svg) Permet d'affiner l'emplacement du stock dans la location en créant des sous-locations |

### ![](https://img.shields.io/badge/-Model-blue.svg) LocationType (table `company_locationtype`)

Définit la typologie des différents emplacements enregistrés dans le système (par exemple : Boutique, Entrepôt, Zone de transit, Palette, etc). Configurables par entreprise dans le panneau de contrôle.

---

# <a id="catalogue">![](https://img.shields.io/badge/-App-darkblue.svg) Catalogue

### ![](https://img.shields.io/badge/-Model-blue.svg) Product (table `catalogue_product`)

Fiche descriptive d'un produit. Centralise les données globales d'identification du produit (comme le code SKU, le code-barre et le nom) ainsi que des champs d'audit. Chaque entreprise a son catalogue de produits.

![](https://img.shields.io/badge/Unique-company__id,_sku-blueviolet.svg)

![](https://img.shields.io/badge/Unique-company__id,_barcode-blueviolet.svg)


| ![](https://img.shields.io/badge/-Field-turquoise.svg) | Note                                                                                                                                                                                                                                  |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| barcode                                                | ![](https://img.shields.io/badge/DEV-VX-green.svg) Fonctionnalité de scan par code barre                                                                                                                                            |
| alert_threshold                                        | ![](https://img.shields.io/badge/DEV-V1-green.svg) Permet de définir un seuil d'alerte global pour ce produit.<br />![](https://img.shields.io/badge/DEV-VX-green.svg) Écrasé  par la configuration par location si elle existe |

### ![](https://img.shields.io/badge/-Model-blue.svg) ProductImage (table `catalogue_productimage`)

Associe une ou plusieurs images à un Produit, incluant la gestion d'une image principale (`is_main`) et des textes alternatifs pour l'accessibilité.

### ![](https://img.shields.io/badge/-Model-blue.svg) ProductConfig (table `catalogue_productconfig`)

Table permettant d'affiner la configuration d'un produit par location. Si une entrée existe pour le produit et la location, elle écrasera les champs équivalents de Produit.

### ![](https://img.shields.io/badge/-Model-blue.svg) ProductPrices (table `catalogue_productprices`)

Regroupe les informations financières d'un produit, par location.

> [!WARNING]
> TODO: Toute la logique sur l'aspect financier doit faire l'objet d'une réflexion plus poussée.

### ![](https://img.shields.io/badge/-Model-blue.svg) Category (table `catalogue_category`)

Structure l'arborescence du catalogue en catégories et sous-catégories de produits, facilitant la classification, la recherche et l'organisation logique des stocks.

![](https://img.shields.io/badge/Unique-name_parent--id-blueviolet.svg)


| ![](https://img.shields.io/badge/-Field-turquoise.svg) | Note                                                                                                                                                                                               |
| :----------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| parent_id                                              | ![](https://img.shields.io/badge/DEV-V1-green.svg) Toujours NULL<br />![](https://img.shields.io/badge/DEV-V2-green.svg) Implémentation de la fonctionnalité pour hiérachiser les catégories |

### ![](https://img.shields.io/badge/-Model-blue.svg) Category (table `catalogue_productcategory`)

Table de jointure permettant d'associer un produit à une ou plusieurs catégories du catalogue.

---

# <a id="inventory"> ![](https://img.shields.io/badge/-App-darkblue.svg) Inventory

### ![](https://img.shields.io/badge/-Model-blue.svg) Stock (table `inventory_stock`)

Représente l'état instantané du stock disponible pour un produit donné à un instant T, strictement isolé et rattaché à une entreprise spécifique.

![](https://img.shields.io/badge/Unique-company__id,_product__id,_location__id-blueviolet.svg)


| ![](https://img.shields.io/badge/-Field-turquoise.svg) | Note                                                                                                                                                                                                                                                                                                                                            |
| ------------------------------------------------------ | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| company_id                                             | Champs en provenance de Product et de Location (qui doivent être = d'ailleurs).<br />Permet de filtrer plus facilement et appliquer la règle d'unicité combinée. Permet aussi de surcharger la méthode `clear()` pour intercepter écriture en DB d'un Produit qu'on tenterait d'assigner à une location qui n'est pas dans sa compagnie. |
| quantity                                               | Ce champs fait l'objet de permissions pointues pour pouvoir être modifiés et chaque modification est enregistrée dans la table`inventory_movement`.                                                                                                                                                                                          |

Dès que les champs `location_id `ou `quantity `changent ou qu'un ligne est ajouté ou supprimé dans `inventory_stock`, un mouvement d'inventaire est enregistré dans la table `inventory_movement`. La classe Stock enregistre des permissions granulaires pour ces actions.

Liste des permissions de mouvement de stocks :

* `PURCHASE` : Approvisionnement / Achat de marchandise
* `MANUFACTURE` : Production interne
* `SALE` : Sortie pour vente
* `LOSS` : Perte, casse ou vol constaté
* `TRANSFER_IN` : Entrée via un transfert inter-location au sein d'une même compagnie
* `TRANSFER_OUT` : Sortie via un transfert inter-location au sein d'une même compagnie
* `INTERN_PURCHASE`: Entrée via un transfert inter-entreprise
* `INTERN_SALE`: Sortie via un transfert inter-entreprise
* `RELOCATE` : Changement d'emplacement au sein de la même location de haut niveau (parent = NULL)

**Direction du mouvement (`movement_direction` ENUM) :**

* `IN` : La quantité est ajoutée au stock courant.
* `OUT` : La quantité est soustraite du stock courant.
* `NONE` : Le niveau global de stock ne change pas (lié à `mouvement.relocate`).

Sécurité

### ![](https://img.shields.io/badge/-Model-blue.svg) Uom(table `inventory_uom`)

Sigle pour "Unit of Measure". Fonctionnalité ajoutée dans la  ![](https://img.shields.io/badge/DEV-V1-green.svg). Avant son intégration, la quantité est toujours considéré comme étant unitaire.

### ![](https://img.shields.io/badge/-Model-blue.svg) Movement (table `inventory_movement`)

Journal d'historique des mouvements d'inventaires.


| ![](https://img.shields.io/badge/-Field-turquoise.svg) | Note                                                                                                                                                         |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| source_location_id                                     | Pour les mouvements internes (inter-location ou inter-company), renseigne la provenance de haut-niveau (`company_location.parent_id = null`) du mouvement   |
| dest_location_id                                       | Pour les mouvements internes (inter-location ou inter-company), renseigne la destination de haut-niveau (`company_location.parent_id = null`) du mouvement |
| unit_price                                             | Permet d'immortaliser la valeur financière du produit au moment du mouvement                                                                                |

---

# <a id="reporting">![](https://img.shields.io/badge/-App-darkblue.svg) Reporting

> [!WARNING]
> TODO: Toute la logique sur l'aspect des rapports et graphiques doit faire l'objet d'une réflexion plus poussée en lien avec les besoins DB

# <a id="others"> Autres fonctionnalités

* Traduction de l'aspect Data
  * `django-parler`?
* Gestion des tiers (fournisseurs et clients):
  * Application `partners `avec modèles Supplier et Customer, lié au modèle `company.Company`
  * Pour le modèle Movement: héritage de modèle ou table d'extension en relation OneToOne.
* Liaison avec des documents justificatifs:
  * Ajout d'un champ `reference_document` ou d'une table dédiée aux commandes/factures permettant de lier le mouvement à sa source légale ou commerciale.
* Traçabilité fine de l'inventaire (lots, numéros de série, date de péremption / expiration) : champs optionnels (null=True, blanc=True)
  * batch_number, serial_number, expiration_date...
* Gestion de déclinaisons de produits (couleur, taille, etc)
* Ajouter la notion de Link entre produits (produits similaires, produits identiques)
  * Links entre produit d'une même compagnie (ok, pas de risque de fuite de données)
  * Links entre produits de compagnie différentes (implique permissions très élevées genre super-user pour modifier les liens et éviter fuite de données)
  * Solution: tous liens--> Apps GlobalCatalogue, réservé aux admin
* Gestion financière
  * Prix de gros, de vente, ect
  * Devises selon les locations
  * Dashboard avec des graphiques sur les états financiers
