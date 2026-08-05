<div align="center">

<img src="../assets/img/logo.svg" alt="Logo Gestion de stocks" width="60" />

# Sécurité des données et contrôle d'accès

Projet Gestion de stocks — document de travail

<img src="https://img.shields.io/badge/Statut_du_document-V1_À_réviser-purple.svg" alt="Statut" />

<h3>

<a href="#analyse">Analyse</a> | <a href="#rbac">Custom RBAC</a> | <a href="#midleware">Middleware</a> | <a href="#manager">Manager</a> | <a href="#permissions">Permissions</a> | <a href="#roles">Roles</a> | <a href="#tests">Tests</a> |

</h3>

</div>

Ce document discute de la sécurité des données et du contrôle d'accès. La première partie analyse et documente les choix techniques réalisés alors que la suite présente la structure du système de contrôle d'accès basé sur les rôles (**RBAC - Role-Based Access Control**) personnalisé et les barrières de sécurité mises en place.

---

## Sommaire

### Modèle d'usage retenu

L'application est centrée sur le scénario principal du cahier des charges : une même instance applicative permet à un ou plusieurs propriétaires métier de gérer les stocks de plusieurs entreprises leur appartenant.

Le projet n'est donc pas conçu, dans sa version actuelle, comme une plateforme SaaS multi-clients où plusieurs organisations indépendantes cohabitent dans la même base de données. Les entreprises présentes en base appartiennent toutes au même propriétaire et donc au même périmètre métier global.

Conséquences :

- un utilisateur propriétaire (`is_owner=True`) a accès à toutes les entreprises présentes en base ;
- les employés (`is_owner=False`) ont des accès limités par un RBAC custom ;
- les données restent rattachées à une compagnie afin de permettre le filtrage, les rapports, les permissions et l'intégrité métier ;
- les vues company-scoped (url /c/company-slug/...) et les vues globales owner (url /g/...) sont explicitement séparées.

### Types d'utilisateurs

| Type                | Champ / mécanisme                   | Portée                                                 |
| ------------------- | ----------------------------------- | ------------------------------------------------------ |
| Propriétaire métier | `User.is_owner=True`                | Accès métier global à toutes les compagnies            |
| Employé             | `User.is_owner=False` + RBAC custom | Accès limité par compagnie, location et permission     |
| Staff technique     | `User.is_staff=True`                | Accès à l'administration Django                        |
| Superuser technique | `User.is_superuser=True`            | Accès technique total, distinct du propriétaire métier |

Le champ `is_owner` ne remplace pas `is_superuser`. Le propriétaire est un rôle métier. Le superuser est un rôle technique lié à l'administration Django.

Un propriétaire peut promouvoir un autre utilisateur propriétaire. L'application doit toujours avoir au moins un propriétaire actif.

Les employés sont des utilisateurs globaux de l'application dont les droits sont limités par le RBAC custom. 

* Un employé peut avoir accès à une ou plusieurs entreprises avec des rôles différents. 

* Un employé peut créer d'autres employés s'il possède la permission adéquate. 
  
  * Cette permission n'inclut jamais le changement de la propriété `user.is_owner`. 

* Un employé peut assigner des rôles à d'autres employés s'il possède la permission adéquate. 
  
  * Cette permission est toujours limitée par son propre périmère autorisé.

### URLs company-scoped et vues globales owner

Les **vues métier liées à une compagnie** utilisent le format suivant :

```text
/c/<company_slug>/...
```

Ces vues sont toujours filtrées sur la compagnie courante, y compris lorsque l'utilisateur est le propriétaire.

Les **vues globales** sont séparées et explicitement réservées aux propriétaires :

```text
/g/...
```

---

## <a id="analyse">1. Analyse

#### RBAC dans django

Django met en oeuvre nativement un contrôle d'accès basé sur les rôles (RBAC) où les concepts de **Permissions** et de **Rôles** sont utilisés comme fondations :

* **Permissions** : Une action précise que l'utilisateur a le droit d'effectuer (ex: *Créer un produit*, *Voir une page*).
  * Django génère automatiquement les 4 permissions CRUD pour chaque modèle (`view`, `add`, `change`, `delete`).
* **Rôles (Groupes)** : Un ensemble de permissions rassemblés sous un même identifiant (ex: *Gestionnaire*, *Magasinier*, *Vendeur*).
  * Django utilise le terme *Group* pour désigner les rôles. Django crée les structures de DB nécessaires mais ne génère aucun rôle par défaut.
* **Assignations** : Les utilisateurs sont assignés aux rôles, ce qui donne automatiquement toutes les permissions associées.
  * Django gère cette relation via une table intermédiaire lié au modèle utilisateur `AUTH_USER_MODEL`. Ces assignations sont *globales à toute la base de données*. Ainsi, un utilisateur ayant le droit de modifier un produit peut modifier n'importe quel produit sans restriction.
* **Concept de super-utilisateur (`is_superuser`)** : Un super-utilisateur possède toutes les permissions existantes et futures indépendamment des rôles et permissions qui lui sont explicitement assignés.
* **Concept d'utilisateur inactif (`is_active`)** : Un utilisateur inactif (`is_active=False`) n'a aucun accès, peu importe les rôles et permissions qui lui sont assignés.
* Concept d'utilisateur employé (`is_staff`) : Un utilisateur « employé » a accès au panneau d'administration natif de django.

#### RBAC pour l'application de Gestion de Stocks

En plus du comportement CRUD standard, cette application de gestion de stocks multi-entreprises impose des contraintes de sécurité spécifiques :

* **Isolation par Entreprise (`Company`):** Un utilisateur possède des permissions distinctes pour chaque entreprise.
  * *Exemple* : un utilisateur peut être *Gestionnaire* et *Vendeur* dans l'Entreprise A et disposer uniquement d'un rôle en *Lecture seule* dans l'Entreprise B.
* **Permissions granulaires**: Certaines permissions ne s'alignent pas sur le modèle CRUD global.
  * *Exemple 1 (Métier)* : Un vendeur a le droit de diminuer l'inventaire lors d'une vente, mais n'a pas le droit de déclarer une perte par bris, ni d'augmenter le stock. Le droit est lié au contexte du mouvement et non au simple droit de modification (`change_stock`) du modèle.
  * *Exemple 2 (Interface)* : un gestionnaire a accès aux graphiques d'alerte de seuil bas mais pas aux graphiques globaux qui rassemblent les données de plusieurs entreprises.
* **Besoin d'aggrégation de données multi-entreprises** : il faut également penser au futur dashboard qui doit rassembler les données de plusieurs entreprises dans une vue résumé, avec des graphiques chart.js.

#### Analyse et limitation

Les permissions natives CRUD de Django lient l'utilisateur et le modèle globalement. Ainsi, le systeme natif de Django ne peut pas, tel quel, répondre aux besoins concernant l'**Isolation par Entreprise** ou les **Permissions granulaires**.

#### RBAC de librairies tierces

Des librairies django existent pour répondre spécifiquement aux besoins de développement d'application django multi-tenant. 

##### Django-guardien

Django-guardian permet d'étendre le système de permissions natif de django afin d'assigner des droits sur des instances précises

| Avantages                                                                                                                                                                              | Inconvénients                                                                                                                                                                                                                              |
|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Granularité extrême** : Permet d'assigner des permissions spécifiques à un utilisateur pour un objet unique (ex: "Julie peut modifier le stock du Produit A mais pas du Produit B"). | **Lourdeur SQL** : Chaque vérification de permission nécessite des jointures complexes ou des requêtes supplémentaires, ce qui peut dégrader les performances à grande échelle                                                             |
| **Interface Admin intégrée** : Ajoute des vues de gestion des permissions directement dans l'interface d'administration de Django.                                                     | **Surcouche inutile pour le besoin actuel** : Pour le projet de gestion de stocks, le besoin est d'avoir des droits fonctionnels (ex: stock.sale) plutôt que des droits par objet individuel. Guardian serait "overkill" dans ce contexte. |
| **Efficacité pour peu de modèles** : C'est une solution robuste pour des permissions par objet sur un ou deux modèles critiques.                                                       | **Complexité de maintenance** : La gestion des tables de permissions génériques (GenericForeignKey) rend le débogage et la maintenance de la base de données plus ardus.                                                                   |

##### Django-tenants

Django-tenants implémente le multi-tenancy en créant des schémas de base de données distincts pour chaque entreprise, en isolant par schémas PostGreSQL.

| Avantages                                                                                                                                                                  | Inconvénients                                                                                                                                                                                                                                            |
|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Isolation de données maximale** : Le cloisonnement au niveau du SGBD garantit qu'un bug applicatif ne peut pas faire fuiter les données d'une entreprise vers une autre. | **Cauchemar des statistiques globales** : Les requêtes croisées entre entreprises (comme pour un dashboard consolidé inter-entreprises pour un propriétaire) sont extrêmement complexes et lentes car elles nécessitent de basculer de schéma en schéma. |
| **Code métier "propre"**: Puisque l'isolation est gérée par le schéma, il n'est pas nécessaire d'ajouter manuellement .filter(company=...) à toutes les requêtes.          | **Incompatibilité MySQL** : Cconçu exclusivement pour PostgreSQL car MySQL ne supporte pas nativement les schémas de la même manière.                                                                                                                    |
| **Sauvegardes indépendantes** : Il est plus simple d'exporter ou de restaurer les données d'un seul client spécifique.                                                     | **Migrations chronophages** : Chaque migrate doit être exécuté sur chaque schéma client. Avec des dizaines d'entreprises, cela devient un processus très lourd.                                                                                          |

Ces bibliothèques Django visent à résoudre les limites du RBAC natif de dnango, mais elles s'avèrent inadaptées à l'architecture MySQL et les besoins d'agrégation. **Django-Guardian** offre une granularité par objet mais impose une complexité SQL inutile pour des droits fonctionnels. De son côté, **Django-Tenants** assure une isolation forte via des schémas PostgreSQL, mais cette approche est techniquement incompatible avec MySQL et rend les calculs statistiques multi-entreprises (nécessaires au dashboard propriétaire) extrêmement inefficaces.

#### Choix du moteur de base de données

Un premier jet de code a été réalisé rapidement en configurant MySQL, déjà fonctionnel sur un environnement de développement local WSL.

Bien que **PostgreSQL** soit souvent la référence pour des projets SaaS dépassant le simple CRUD en raison de ses fonctions d'isolation (RLS) et sa robustesse, le choix choix de **MySQL** se justifie pleinement par :

1. **L'environnement existant :** Le gain de temps immédiat pour le POC.
2. **L'agrégation multi-entreprises :** Sous MySQL, les données partagées facilitent les agrégations SQL natives pour les tableaux de bord Chart.js.
3. **L'approche pédagogique :** Coder  la sécurité par ligne (Row-level) via un middleware et un Manager Django compense l'absence de RLS native de MySQL et permet de démontrer une certaine maîtrise technique pour un projet portfolio.

#### Conclusion

Pour répondre aux exigences d'**Isolation par Entreprise**, de **Permissions granulaires**, le système natif RBAC de Django ne suffit pas. Au vu des objectifs pédagogiques du projet et de la nécessité de produire des rapports consolidés performants via Chart.js, l'utilisation de solutions de librairie tierce sont également écartées. 

La solution retenue est de concevoir et coder un système RBAC personnalisé utilisant une architecture de base de données partagée. Pour prévenir tout risque de fuite de données, cette approche sera sécurisée par des garde-fous rigoureux : un middleware injectant systématiquement le contexte de l'entreprise et un Manager personnalisé filtrant automatiquement tous les QuerySets.

---

## <a id="rbac">2. Custom RBAC

L'application utilise Django `Auth `pour l'identité, l'authentification, les sessions et l'infrastructure utilisateur.

Les permissions métier sont gérées par un système custom dans l'application `access`.

Le `PermissionService` est responsable de répondre à la question :

```text
Cet utilisateur peut-il effectuer cette action dans ce contexte?
```

Règle générale :

- si l'utilisateur est propriétaire, les permissions métier sont accordées ;
- sinon, les permissions sont évaluées à partir des rôles RBAC assignés à l'utilisateur;
- les permissions techniques Django restent distinctes des permissions métier.

### Descriptions des modèles

- **`access_permission`** : Stocke les permissions fonctionnelles de l'application (ex: `codename = "inventory.movement.sale"`). Contrairement au CRUD global de Django, ces permissions décrivent des actions métiers précises.
- **`access_role`** : Regroupe un ensemble de permissions sous un identifiant unique (`slug`).
  - *Clé stratégique* : Le champ `company_id FK (NULLABLE)`. S'il est `NULL`, le rôle est **global** (ex: le rôle *Gestionnaire* existe pour toutes les entreprises). S'il est renseigné, le rôle est  spécifique à une seule entreprise.
- **access_rolepermissions** (**Liste des permissions d'un rôle**) : Permet de définir les permissions associées à chaque rôle.
- **`users_userrole` (Table d'assignation dynamique)** : C'est le cœur du système. Elle associe un utilisateur à un rôle, mais y ajoute un **scope (périmètre de validité)** :
  - Si `company_id` et `location_id` sont `NULL`, l'utilisateur possède ce rôle de manière globale.
  - Si `company_id` est renseigné, le rôle et ses permissions ne s'appliquent *qu'au sein de cette entreprise*.
  - Si `location_id` est renseigné, les droits sont restreints à un entrepôt ou un emplacement physique spécifique (granularité maximale).
- **`access_log` (Piste d'audit / Journalisation)** : Enregistre de manière immuable chaque action de modification sur le système d'accès (création de rôle, changement de permissions). Elle utilise un champ `JSONField` (`changes`) pour stocker l'état avant/après, garantissant une traçabilité totale exigée par la gestion de stocks multi-entreprises.

### Méthode pour vérifier les permissions

```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # ... Les champs personnalisés...

    def has_location_perm(self, company_id, permission_codename, location_id=None):
        """
        Vérifie si l'utilisateur possède une permission spécifique pour une entreprise
        et optionnellement pour un emplacement (location) donné.
        """
        # Un utilisateur inactif n'a aucun droit, peu importe ses rôles ou statuts
        if not self.is_active:
            return False

        # Court-circuit : un super-utilisateur ou le propriétaire possède tous les accès
        if self.is_superuser or self.is_owner:
            return True

        # Construction des filtres de scope pour la table intermédiaire
        # L'utilisateur a accès si le rôle est global (NULL) OU correspond exactement à l'entreprise
        company_filter = models.Q(company_id__isnull=True) | models.Q(company_id=company_id)

        if location_id:
            # Si une localisation est demandée, le scope doit être global (NULL) OU correspondre à cette localisation
            location_filter = models.Q(location_id__isnull=True) | models.Q(location_id=location_id)
        else:
            # Si aucune localisation n'est spécifiée, on ne valide que les assignations globales au niveau de l'entreprise
            location_filter = models.Q(location_id__isnull=True)

        # Requête optimisée qui traverse les relations :
        # User -> UserRole -> Role -> Permissions
        return self.userrole_set.filter(
            company_filter,
            location_filter,
            role__permissions__codename=permission_codename
        ).exists()
```

#### Application dans les Vues Django :

```python
# Exemple 1 : Action globale (Ajout d'un produit au catalogue de l'entreprise)
if not request.user.has_location_perm(current_company_id, 'catalogue.product.add'):
    raise PermissionDenied()

# Exemple 2 : Action localisée (Enregistrement d'une perte dans la Boutique B)
if not request.user.has_location_perm(current_company_id, 'inventory.stockloss', location_id=target_location_id):
    raise PermissionDenied()
```

---

## <a id="middleware"> 3. CompanyMiddleware

`CompanyMiddleware `sert à établir le **contexte d'entreprise courante** pour les URLs company-scoped

Responsabilités :

1. détecter les URLs contenant un slug d'entreprise (/c/<company_slug>/...) ;

2. charger la compagnie correspondante ;

3. vérifier que la compagnie est active ;

4. vérifier que l’utilisateur peut accéder à cette compagnie :
   
   * is_owner=True : accès autorisé ;
   * sinon : accès seulement si RBAC donne accès à cette compagnie ;

5. attacher la compagnie à la requête : 

```python
   request.company = company
```

6. définir le contexte utilisé par `CompanyScopedManager `;

7. nettoyer ce contexte après la requête.

`CompanyMiddleware` vérifie l'accès à la compagnie mais il ne remplace pas les permissions métier granulaires. Les actions comme modifier un produit, ajuster un stock ou créer un employé doivent être validées par le `PermissionService`.

---

## <a id="manager"> 4. CompanyScopedManager

Les modèles rattachés à une compagnie utilisent un manager filtrant, nommé `CompanyScopedManager`. `CompanyScopedManager `filtre automatiquement les modèles rattachés à une compagnie selon le contexte courant.

Ainsi, 

```python
Product.objects.all()
```

dans l'url `/c/company-a/products/` retournera seulement les produits de l'entreprise dont le slug est *company-a*. À noter qu'une vue *company-scoped* reste *company-scoped* même pour le propriétaire (qui a le droit de tout voir mais à partir d'autres vues!).

Les vues globales owner doivent utiliser des accès explicites et protégés, et non contourner implicitement le filtrage dans les vues company-scoped.

---

## <a id="permissions">5. Référentiel des permissions

Les permissions sont créées lors de la configuration initiale de l'application. 

Les permissions suivent le modèle suivant: *[app_name].[model_name].[OPT context][perm_type]*.

- *perm_type* reprend les CRUD officiels de django (`view`, `add`, `change`, delete`) `et les étend en les regroupant parfois l (ex: `manage`) ou en ciblant un champs spécifique (ex: `activate `dans `users.user.activate`  permet de mettre le field `is_active `de l'utilisateur à vrai)

- *model_name* est parfois sauté car la permission concerne plusieurs tables (ex: `access.manage` permet de faire des changements dans les tables `access_role `et `access_rolepermissions`)

- *context* est optionnel et est utilisé pour quelques permissions (ex: `company.location.main.add` et `company.location.sub.add` permettent respectivement de créer (ou non) des emplacements de haut niveau (`parent_id `= NULL) et des emplacements de sous-location (`parent_id` = ID de la location parent)

> [!TIP]
> *Les fonctionnalités sous-jacentes à chaque permission seront implémentées à différents stades du développement. Certaines permissions sont projetées mais pourraient être codé différemment selon l'évolution du produit et de l'UX.*

#### Périmètre

Défini si le périmètre de la permission est global ou `company-scoped`. Les libellés NEVER et owner sont aussi utilisés pour décrire qui peut réaliser l'action décrite. 

| Périmètre | Description                                                                                                                                                                                                                                                                                         |
|:--------- |:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| global    | La permission s'applique dans un contexte multi-entreprises (owner ou employé de haut rang)                                                                                                                                                                                                         |
| company   | La permission s'applique exclusivement dans un contexte d'entreprise active.                                                                                                                                                                                                                        |
| NEVER     | Cette permission ne sera **PAS** créée car elle est bloquée / impossible pour tous les utilisateurs finaux du front-end ou listée / regroupée sous un autre nom. Il s'agit la plupart du temps de permissions CRUD de django dont on documente la raison pour laquelle elle ne sera pas codé ainsi. |
| owner     | La permission est normalement accessible uniquement au propriétaire (`user.is_owner = True`) mais peut être déléguée par permission si associée à un rôle. À noter que le propriétaire a accès à toutes les permissions sans besoin d'yb être explicitement assigné via un rôle (*bypass* direct).  |

### 5.1. ![](https://img.shields.io/badge/-App-darkblue.svg) Core (`core.*`)

Centralise les configurations globales du système.

| Code (`codename`)                            | Description (`name`)                                                                                                                           | Périmètre          |
|:-------------------------------------------- |:---------------------------------------------------------------------------------------------------------------------------------------------- | ------------------ |
| ~~`core.settings.add`~~                      | Ajouter une configuration globale. *La table core.settings ne contient qu'un seul enregistrement.*                                             | NEVER              |
| `core.settings.view`                         | Consulter les configurations globales                                                                                                          | global, owner-only |
| `core.settings.change`                       | Modifier les configurations globales                                                                                                           | global, owner-only |
| ~~`core.settings.delete`~~                   | Supprimer les configuration globales. *La table core.settings doit contenir un seul enregistrement.*                                           | NEVER              |
| ~~`core.image.[view\|add\|change\|delete]`~~ | Gérer les images. *Les images sont gérées à partir des permissions du modèle lié (ex: image de profil de User si tu peux modifier le profil.)* | NEVER              |

### 5.2. ![](https://img.shields.io/badge/-App-darkblue.svg) Users (`users.*`)

Gère les profils utilisateurs et leur accès.

| Code de permission                                                                       | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Périmètre          |
|:---------------------------------------------------------------------------------------- |:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------ |
| `users.add`                                                                              | Créer un nouvel utilisateur dans le système.<br/> - Le champs `is_owner `est bloqué et fixé à False en tout temps.                                                                                                                                                                                                                                                                                                                                                     | global             |
| users.user.invite                                                                        | Inviter un utilisateur à créer son propre compte à partir d'un courriel contenant un lien sécurisé                                                                                                                                                                                                                                                                                                                                                                     | global             |
| `users.user.view`                                                                        | Voir la liste des utilisateurs <mark>TODO</mark>. Comment faire en sorte qu'un gestionnaire (par exemple) voit seulement la liste des utilisateurs affectés à son secteur d'activité?                                                                                                                                                                                                                                                                                  | global             |
| `users.user.change`                                                                      | Modifier les informations ou préférences de n'importe quel utilisateur, exluant le statut d'activation du compte (`user.is_active`) et le drapeau propriétaire (`user.is_owner`)<br/> <mark>TODO</mark>. Comment permettre à un gestionnaire de modifier seulement les utilisateurs de son entreprise et/ou de sa location ? Il faudrait vérifier les permissions de tous les employés et filtrer ceux qui sont dans le (s) même(s) périmètre(s)  que lui (possible ?) | global             |
| `users.user.change_own`                                                                  | Modifier les informations et préférences de son propre profil (exclut les champs `user.is_active` et `user.is_owner`)                                                                                                                                                                                                                                                                                                                                                  | global             |
| `users.user.delete`                                                                      | Supprimer un utilisateur (le système refusera si au moins une référence à cet utilisateur existe)                                                                                                                                                                                                                                                                                                                                                                      | global             |
| `users.user.activate`                                                                    | Réactiver le compte d'un utilisateur (set `user.is_active = True`)                                                                                                                                                                                                                                                                                                                                                                                                     | global             |
| `users.user.inactivate`                                                                  | Désactiver le compte d'un utilisateur d'un utilisateur (set `user.is_active = False`)                                                                                                                                                                                                                                                                                                                                                                                  | global             |
| ~~`users.userrole.add`~~<br/>~~`users.userrole.change`~~<br/>~~`users.userrole.delete`~~ | Assigner, modifier ou supprimer les rôles d'un utilisateur. Regroupement sous une seule permission `users.userrole.manage`                                                                                                                                                                                                                                                                                                                                             | NEVER              |
| `users.userrole.view`                                                                    | Consulter les rôles assignés à une liste d'utilisateurs (<mark>TODO</mark>: idem questionnement que pour user.view)                                                                                                                                                                                                                                                                                                                                                    | global             |
| `users.userrole.manage`                                                                  | Assigner, modifier ou supprimer les rôles assignés à un utilisateur. (<mark>TODO</mark>: idem questionnement que pour user.change) <mark>Autre TODO IMPORTANT: </mark> Un utilisateur avec cette permission ne doit pas pouvoir assigner des permissions qu'il n'a pas lui-même.                                                                                                                                                                                       | global             |
| users.userrolelog.view                                                                   | Voir l'historique des modifications sur les assignations de rôle                                                                                                                                                                                                                                                                                                                                                                                                       | global, owner-only |
| ~~`users.userrolelog.[add\|change\|delete]`~~                                            | Log en lecture seule.                                                                                                                                                                                                                                                                                                                                                                                                                                                  | NEVER              |

### 5.3. ![](https://img.shields.io/badge/-App-darkblue.svg) Company (`company.*`)

Pilote les entreprises et cartographie l'infrastructure physique (location, sous-locations et types de location).

| Code de permission                                     | Description                                                                                                                                                                                                                                                                      | Périmètre           |
|:------------------------------------------------------ |:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |:------------------- |
| `company.company.view`                                 | Voir les informations de configuration de l'entreprise.                                                                                                                                                                                                                          | company             |
| ~~`company.company.add`~~                              | Créer une nouvelle entreprise.                                                                                                                                                                                                                                                   | owner-only          |
| ~~`company.company.change`~~                           | Modifier les informations de l'entreprise, exluant l'archivage.                                                                                                                                                                                                                  | company, OWNER-ONLY |
| ~~`company.company.archive`~~                          | Archiver ou désarchiver l'entreprise<br/>Une entreprise archivée `(is_archive = True`) n'est plus disponible pour aucune action (création de produit, modification d'inventaire, etc) et n'apparaît plus dans le tableau de bord et les rapports [Est en consultation seulement] | company, OWNER-ONLY |
| ~~`company.company.delete`~~                           | Supprimer une entreprise.  Cette action est irréversible et supprime l'entreprise, toutes les références et tout l'historique associé à l'entreprise.                                                                                                                            | company, OWNER-ONLY |
| ~~`company.locationtype.[view, add, change, delete]`~~ | Ajouter, modifier et supprimer les types de location. *Géré  par `company.locationtype.manage`* et  *seulement voir les locationtype n'est pas pertinent.*                                                                                                                       | NEVER               |
| `company.locationtype.manage`                          | Gérer les types de location (ajouter, modifier et supprimer)                                                                                                                                                                                                                     | company, owner      |
| `company.location.view`                                | Consulter la cartographie hiérarchique des emplacements                                                                                                                                                                                                                          | company             |
| `company.location.main.add`                            | Créer un emplacement de haut niveau (emplacement racine) et définir son adresse, son type et ses paramètres.                                                                                                                                                                     | company, owner      |
| `company.location.main.change`                         | Modifier les informations d'un emplacement de haut niveau (type, nom, adresse,    , etc).                                                                                                                                                                                        | company, owner      |
| `company.location.main.delete`                         | Supprimer un emplacement de haut niveau (emplacement racine). Le système empêchera la suppression si des références à cet emplacement existe (stock)                                                                                                                             | company, owner      |
| ~~`company.location.sub.[view\|add\|change\|delete]`~~ | Voir ou gérer des sous-locations. *Géré par `company.location.view` et `company.location.sub.manage`*                                                                                                                                                                            | NEVER               |
|                                                        |                                                                                                                                                                                                                                                                                  |                     |
| `company.location.sub.manage`                          | Gérer les sous-locations (emplacements enfants). À la création / mise à jour, le système doit vérfier que le parent choisi appartient bien à la même entreprise. Aussi, le système empêchera la suppression si des références (stock) y font référence.                          | company             |
| company.import                                         | Importer massivement les données d'une entreprise, incluant les infos de locations, le catalogue et l'inventaire (CSV). <mark>TODO </mark>Comment gérer si la company contient déjà des données?                                                                                 | company, owner      |
| company.export                                         | Exporter les données d'une entreprise, incluant les infos de locations, le catalogue et l'inventaire (CSV).                                                                                                                                                                      | company, owner      |

### 5.4. ![](https://img.shields.io/badge/-App-darkblue.svg) Catalogue (`catalogue.*`)

Structure le référentiel des articles disponibles à la gestion de stock.

| Code de permission                             | Description                                                                                                                                                                                                      | Périmètre |
|:---------------------------------------------- |:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |:--------- |
| `catalogue.product.view`                       | Consulter le catalogue des produits (inclut les infos des modèles de produit, leurs variantes. leurs catégories et leurs images associées. Exlut les infos de configuration).                                    | company   |
| `catalogue.product.add`                        | Créer un nouveau produit (inclut les modèles de produit, leurs variantes. leurs catégories et leurs images associées. Exclut la les infos de configuration et l'archivage).                                      | company   |
| `catalogue.product.change`                     | Modifier les caractéristiques d'une fiche produit (inclut les modèles de produit, leurs variantes. leurs catégories et leurs images associées. Exclut la mise à jour des infos de configuration et l'archivage). | company   |
| `catalogue.product.archive`                    | Archiver ou désarchiver un produit. *Un modèle archivé va archiver toutes ses variantes. Une variante archivée n'affecte pas son modèle.*                                                                        | company   |
| `catalogue.product.delete`                     | Supprimer définitivement un produit du catalogue de l'entreprise. *Le système bloquera la suppression si des référence au produit existe.*                                                                       | company   |
| `catalogue.category.view`                      | Consulter l'arborescence complète des catégories.                                                                                                                                                                | company   |
| ~~`catalogue.category.[add\|change\|delete]`~~ | Ajouter, modifier ou supprimer une catégorie ou sous-catégorie. *Gérer par `catalogue.category.manage`*                                                                                                          | NEVER     |
| `catalogue.category.manage`                    | Modifier ou réorganiser la hiérarchie des catégories. Le système bloquera la suppression d'une catégorie référencée dans les produits                                                                            | company   |

### 5.5. ![](https://img.shields.io/badge/-App-darkblue.svg) Inventory (`inventory.*`)

Gère l'état des stocks réels et encadre rigoureusement les modifications aux quantités  en inventaire.

| Code de permission                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Description                                                                                                        | Périmètre (context et is_sensible) |
|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |:------------------------------------------------------------------------------------------------------------------ |:---------------------------------- |
| ~~`inventory.uom.[view\|add\|change\|delete]`~~                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | Géré par la permission inventory.uom.manage                                                                        | NEVER                              |
| `inventory.uom.manage`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | Gérer les unités de mesure utilisés dans l'inventaire.                                                             | company                            |
| `inventory.stock.view`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | Consulter les niveaux de stock disponibles par emplacement.                                                        | company                            |
| `inventory.movement.view`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Consulter le journal historique des mouvements de stock.                                                           | company                            |
| ~~`inventory.movement.[add\|change\|delete]`~~                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | Le journal est en lecture seule                                                                                    | NEVER                              |
| ~~`inventory.stock.[add\|change\|delete]`~~                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | Gérer le stock. La gestion du stock se fait par des permissions plus granulaires sur le champs `quantity`.         | NEVER                              |
| ~~`inventory.movementreason.[view\|add\|change\|delete]`~~                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Gérer les raisons pour modifier les quantités en inventaire. Se fait par une permission générale (`manage`)        | NEVER                              |
| <a id="permissions-reasons">`inventory.movementreason.manage`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | Gérer les raisons pour modifier les quantités en inventaire.                                                       | company,  owner                    |
| `inventory.movementreason.increase`<br/>*Permet tous les mouvements d'augmentation d'inventaire peu importe leur raison.*<br/>Ex:<br/>*- stock.quantity est augmenté*<br/>*- un movement est créé avec location_source NULL et location_dest NULL*                                                                                                                                                                                                                                                                                                                                                                                                                                             | Augmenter l'inventaire (permission générique)                                                                      | company, movementreason            |
| `inventory.movementreason.decrease`<br/>*Permet tous les mouvements de diminution d'inventaire, peu importe la raison.*<br/>Ex:<br/>*- stock.quantity est diminué*<br/>*- un movement est créé avec location_source NULL et location_dest NULL*                                                                                                                                                                                                                                                                                                                                                                                                                                                | Diminuer l'inventaire (permission générique)                                                                       | company, movementreason            |
| `inventory.movementreason.purchase`<br/>*Ex: T-Shirt d'un fournisseur est reçu dans la zone de réception de marchandises.*<br/>*- stock.quantity est augmenté*<br/>*- un movement est créé avec location_source NULL et location_dest qui pointe vers la location modifiée.*                                                                                                                                                                                                                                                                                                                                                                                                                   | Augmenter l'inventaire en raison d'une commande d'achat à un fournisseur.                                          | company, movementreason            |
| `inventory.movementreason.manufacture`<br/>*Ex: T-Shirt sort de la fabrique et est stocké dans l'entrepôt.*<br/>*- stock.quantity est augmenté*<br/>*- un movement est créé avec location_source NULL et location_dest qui pointe vers la location modifiée.                                                                                                                                                                                                                                                                                                                                                                                                                                   | Augmenter l'inventaire en raison de l'arrivée de produits issues d'une chaîne de production interne.               | company, movementreason            |
| `inventory.movementreason.sale`<br/>*Ex: T-Shirt est vendu.*<br/>*- stock.quantity est diminué*<br/>*- un movement est créé avec location_source pointant vers la location modifié et location_dest NULL.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Diminuer l'inventaire en raison d'une vente.                                                                       | company, movementreason            |
| `inventory.movementreason.count_more`<br/>*Ex: Le nombre de T-Shirt sur l'étagère A est plus élevé que la quantité indiquée en inventaire.*<br/>*- stock.quantity est augmenté*<br/>*- un movement est créé avec location_source et location_dest pointant vers la location modifiée.*                                                                                                                                                                                                                                                                                                                                                                                                         | Augmenter l'inventaire en raison d'un ajustement de décompte d'inventaire.                                         | company, movementreason            |
| `inventory.movementreason.count_less`<br/>*Ex: Le nombre de T-Shirt sur l'étagère B est plus basse que la quantité indiquée en inventaire.*<br/>*- stock.quantity est diminué*<br/>*- un movement est créé avec location_source et location_dest pointant vers la location modifiée.*                                                                                                                                                                                                                                                                                                                                                                                                          | Diminuer l'inventaire en raison d'un ajustement de décompte d'inventaire.                                          | company, movementreason            |
| `inventory.movementreason.loss`<br/>*Ex: Un T-Shirt sur l'étagère C est déchiré et donc retiré du stock courant.*<br/>*- stock.quantity est diminué*<br/>*- un movement est créé avec location_source pointant vers la location modifié et location_dest est NULL.*                                                                                                                                                                                                                                                                                                                                                                                                                            | Diminuer l'inventaire en raison de marchandises perdues (bris, vol, date de péremption dépassé, etc).              | company, movementreason            |
| `inventory.movementreason.uom_pack`<br/>*Ex: 10 T-Shirt sont retirés de la tablette et placer dans une boîte pour une vente par pack plutôt que unitaire.*<br/>*- stock.quantity avec uom unit unit est diminué* <br/>*- stock.quantity avec uom unit pack est augmenté* <br/>*- un movement est créé avec location_source du premier changement et location_dest du deuxième changement. quantity_delta est 0.*                                                                                                                                                                                                                                                                               | Diminuer l'inventaire en raison d'un changement d'unité de mesure.                                                 | company, movementreason            |
| `inventory.movementreason.uom_unpack`<br/>*Ex: 10 T-Shirt sont retirés d'une boîte de fournisseur et placer sur la tablette pour renflouer l'emplacement.*<br/>*- stock.quantity avec uom unit parck est augmenté* <br/>*- stock.quantity avec uom unit unit est diminué* <br/>*- un movement est créé avec location_source du premier changement et location_dest du deuxième changement. quantity_delta est 0.*                                                                                                                                                                                                                                                                              | Augmenter l'inventaire en raison d'un changement d'unité de mesure.                                                | company, movement reason           |
| `inventory.movementreason.relocate`<br/>*Ex: 1 T-Shirt est déplacé de l'emplacement Tablette A et placé dans l'emplacement  Lift 12.*<br/>*- stock.quantity de Tablette A est diminué* <br/>*- stock.quantity de Lift 12 est augmenté* <br/>*- un movement est créé avec location_source du premier changement et location_dest du deuxième changement. quantity_delta est 0.*                                                                                                                                                                                                                                                                                                                 | Diminuer l'inventaire pour le relocaliser dans un emplacement ayant le même parent principal.                      | company, movementreason            |
| `inventory.movementreason.transfer_out`<br/>*Ex: 10 T-Shirt sont retirés de l'emplacement Zone Emballage de l'Entrepôt X pour être envoyés à Boutique ABC. Boutique ABC et Entrepôt X sont deux emplacements de haut niveau de la même entreprise. <br/>- Dans stock: qty est diminué de 10.<br/>- Dans movement: nouvelle entrée avec location_source pointant vers la Zone d'emballage de Entrepôt X et location_destination est NULL<br/>- Dans transit: nouvelle entrée avec les mêmes company_id (source et dest) et uom_id (source et dest). location_source_id pointe vers Entrepôt X, location_dest_id pointe vers Boutique ABC, quantity_received est NULL et is_complete est False.* | Diminuer l'inventaire pour l'envoyer dans un emplacement ayant un parent principal différent                       | company, movement reason           |
| `inventory.movementreason.transfert_in`<br/>*Ex: 10 T-Shirt sont réceptionnés à Boutique ABC à partir du transit barcode (ou en sélectionnant la ligne du produit après avoir ouvert transit. <br/><br/>- Dans transit: entrée est mise à jour avec info du destinataire et, qté reçue et est marqué comme complété.* <br/>- Dans stock: qty est augmenté de 10.<br/>- Dans movement: nouvelle entrée avec location_source NULL et location_destination pointe vers Boutique ABC<br/>                                                                                                                                                                                                          | Augmenter l'inventaire pour l'envoyer dans un emplacement ayant un parent principall différent                     | company, movement reason           |
| `inventory.movementreason.intercompany_out`<br/>*Ex: 10 T-Shirt sont retirés de l'emplacement Zone Emballage de l'Entrepôt X pour être envoyés à Entreprise Z. Entrepôt X et Entreprise Z sont deux entreprises indépendantes appartenant au même propriétaire <br/>- Dans stock: qty est diminué de 10.<br/>- Dans movement: nouvelle entrée avec location_source pointant vers la Zone d'emballage de Entrepôt X et location_destination est NULL<br/>- Dans transit: nouvelle entrée avec les infos de source et company_dest pointant vers Entreprise Z. location_dest, uom_dest et quantity_received sont NULL. is_complete est False.*                                                   | Diminuer l'inventaire en raison d'une vente interne vers une entreprise du même propriétaire.                      | company, movementreason            |
| `inventory.movementreason.intercompany_in`<br/>*Ex: 10 T-Shirt sont réceptionnés à Entrepôt X à partir du transit barcode (ou en sélectionnant la ligne du produit après avoir ouvert la liste des transit. <br/>Dans transit: qté reçue et uom_dest sont mis à jour et is_completed est passé à True.* <br/>*- Dans stock: qty est augmenté de 10.*<br/>*- Dans movement: nouvelle entrée avec location_source NULL et location_destination pointe vers Entrepôt X (ou un emplacement interne d'Entrepôt X)*                                                                                                                                                                                  | Augmenter l'inventaire en raison de l'achat (la réception) interne de stock d'une entreprise du même propriétaire. | company, movementreason            |

### 5.6. ![](https://img.shields.io/badge/-App-darkblue.svg) Reporting (`reporting.*`)

Pilote l'accès aux rapports et graphiques, par entreprise et globaux. 

Exemple de rapports qui pourraient être (éventuellement) possible

- Stock total par compagnie

- Produits faibles en stock dans toutes les compagnies

- Mouvements récents toutes compagnies

- Valeur totale du stock

- Comparaison des ventes/sorties

- Transferts en transit inter-company

<mark>TODO</mark>: À réfléchir / définir plus tard.

| Code de permission                    | Description                                                                | Périmètre |
|:------------------------------------- |:-------------------------------------------------------------------------- |:--------- |
| ~~`reporting.[add\|change\|delete]`~~ | Tous les rapports sont en lecture seule                                    | NEVER     |
| reporting.multicompany.view           | Lecture des rapports rassemblant les données de plusieurs entreprises      | global    |
| `reporting.stock_levels.view`         | Lecture des rapports de rotations, ruptures imminentes et seuils d'alerte. | company   |
| reporting.stock_level.view            | ...                                                                        |           |

### 5.7. ![](https://img.shields.io/badge/-App-darkblue.svg) Access (`acces.*`)

Configure les rôles de l'application

| Code de permission                                                                                              | Description                                                                                                                                                                                  | Périmètre |
|:--------------------------------------------------------------------------------------------------------------- |:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |:--------- |
| ~~`access.permission.add`~~<br/>~~`access.permission.change`~~<br/>~~`access.permission.delete`~~               | Changer les  informations de la table des permissions. *Impossible car chaque permission est associée à un comportement d'accessibilité codé en dur.*                                        | NEVER     |
| ~~`access.permission.view~~`                                                                                    | Voir les informations de la table des permissions. Jamais parce que la permission `access.manage` implique nécessairement un accès en lecture et un accès en lecture seul n'a pas d'utilité. | NEVER     |
| ~~`access.role.[view\|create\|change\|delete]`~~<br/>~~`access.rolepermission.[view\|create\|change\|delete]`~~ | Tous regroupés sous `access.manage`                                                                                                                                                          | NEVER     |
| `accces.manage`                                                                                                 | Gérer les rôles et leur association avec des permissions                                                                                                                                     | global    |

### 5.8. Actions réservé au propriétaire

Certaines actions nécessitent la permission `is_owner = True` et ne peuvent pas être déléguées. Ces actions n'ont pas de permissions associées dans le référentiel des permissions. 

* Créer/Supprimer/Archiver une entreprise

* Promouvoir un utilisateur  comme propriétaire (co-propriété)

* Révoquer un utilisateur comme propriétaire
  
  * Possible seulement s'il existe au moins un autre propriétaire
  
  * Un propriétaire ne peut pas se révoquer lui-même

---

## <a id="roles">6. Rôles par Défaut

Lorsqu'une nouvelle entreprise (`Company`) est initialisée dans le système, le système génère des rôles prédéfinis pour cette organisation. Le propriétaire de l'entreprise peut ensuite personnaliser ces rôles et les permissions qui leur sont affectées.

#### A. Gestionnaire

Responsable de l'approvisionnement, de la justesse des inventaires physiques et de la configuration du catalogue d'articles locaux.

* **Permissions affectées** :
  * <mark>TODO</mark>

#### B. Employé

Profil terrain dédié aux tâches logistiques quotidiennes : réception, rangement et expédition. Il ne peut pas modifier les fiches produits ni déclarer des pertes sèches sans validation.

* **Permissions affectées** :
  * <mark>TODO</mark>

#### D. Lecture seule

Profil de consultation destiné au suivi de la santé financière, à la valorisation des stocks et aux inventaires comptables de fin d'année.

* **Permissions affectées** :
  * <mark>TODO</mark>

---

## <a id="tests">7. Tests de sécurité

Les tests de sécurité doivent couvrir au minimum :

- un propriétaire peut accéder à toutes les compagnies ;
- un propriétaire ne voit que la compagnie courante dans une vue `/c/<company_slug>/...` ;
- un employé ne peut accéder qu'aux compagnies autorisées ;
- un employé ne peut pas accéder aux vues globales `/g/...` ;
- un employé autorisé peut créer un autre employé ;
- un employé ne peut pas créer, modifier ou désactiver un propriétaire ;
- il est impossible de désactiver le dernier propriétaire actif ;
- il est impossible d'obtenir un état sans propriétaire actif ;
- les modèles company-scoped ne retournent jamais des données hors scope courant ;
- les vues globales owner sont explicitement protégées par `is_owner=True`.

#### Tests owner

- owner peut accéder à /c/company-a/...;

- owner peut accéder à /c/company-b/...;

- owner peut accéder à /g/dashboard/;

- owner voit les rapports consolidés ;

- owner peut gérer les rôles ;

- owner peut créer une compagnie ;

- owner peut voir les mouvements de toutes les compagnies dans une vue globale.

#### Tests employés

- employé de A peut accéder à A ;

- employé de A ne peut pas accéder à B ;

- employé de A ne peut pas accéder à /g/...;

- employé multi-company peut accéder à A et B ;

- employé avec location limitée ne voit pas les autres locations ;

- employé sans permission stock ne peut pas modifier stock.

#### Tests contexte

- sur /c/company-a/..., même owner voit par défaut les données de A seulement ;

- sur /g/..., seulement owner peut utiliser les querysets globaux ;

- sans contexte company/global explicite, les requêtes échouent.
