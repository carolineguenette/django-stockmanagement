<div align="center">

<img src="../assets/img/logo.svg" alt="Logo Gestion de stocks" width="60" />

# Contrôle d'accès (RBAC) et sécurité des données

Projet Gestion de stocks — document de conception

![Statut](https://img.shields.io/badge/Statut_du_document-En_cours_de_rédaction-purple.svg)

<h3>

[RBAC personnalisé](#rbac) | [Permissions](#permissions) | [Roles](#roles) | [Architecture ](architecture)| [Custom Managers](#manager) |[CompanyMiddleware](#middleware) |  [Intégrité inter-compagnies](integrity) | [Sécurisation endpoints](#endpoints) |[Thread-Safety](#thread-safety)  | [Tests](#tests)

</h3>

</div>

Ce document discute de la sécurité des données et du contrôle d'accès et présente la structure du système de contrôle d'accès basé sur les rôles (**RBAC - Role-Based Access Control**) personnalisé et les barrières de sécurité qui seront mises en place.

[← Analyse](3-choices-and-analysis.md) | [Sommaire](2-conception.md) |  [Modules →](5-django-apps-and-urls.md)

---

## RBAC personnalisé <a id="rbac"></a>

Les permissions métier sont gérées par un système custom. Les modèles sont définis dans l'application `access` alors que le modèle permettant d'assigner un rôle à un utilisateur appartient à l'application `users`.

### Descriptions des modèles du contrôle d'accès

<img src="schema_database_access.svg" alt="Schema access tables" width=400 />
<img src="schema_database_userrole.svg" alt="Schema userrole table" width=400 />

| table                    | Description                                                                                                                                                                                                                                                                                                           |
|:------------------------ |:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `access_permission`      | Stocke les permissions fonctionnelles de l'application (ex:`codename = "inventory.movement.sale"`). Contrairement au CRUD global de Django, ces permissions décrivent des actions métiers précises. Chaque permission s'applique dans un certain contexte (`access_permission.context`) défini ci-bas.                |
| `access_role`            | Regroupe un ensemble de permissions sous un identifiant unique<br/><br/>** Clé stratégique** : Le champ `company_id FK (NULLABLE)`. S'il est `NULL`, le rôle est **global** (ex: le rôle *Gestionnaire* existe pour toutes les entreprises). S'il est renseigné, le rôle est spécifique à une seule entreprise.       |
| `access_rolepermissions` | **Liste des permissions d'un rôle**<br/> Table d'association entre les permissions et les rôles. Permet de définir les permissions associées à chaque rôle.                                                                                                                                                           |
| `access_log`             | **Audit** <br/>Enregistre de manière immuable chaque action de modification sur le système d'accès (création de rôle, changement de permissions). Elle utilise un champ `JSONField` (`snap_infos`) pour stocker les infos au moment de la transaction et des FK pour permettre la recherche / filtre plus facilement. |
| `users_userrole`         | **Table d'assignation**<br/> Cœur du système. Elle associe un utilisateur à un rôle, et y ajoute aussi un **scope (périmètre de validité)**.                                                                                                                                                                          |
| users_userrolelog        | **Audit**<br/>Enregistre de manière immuable chaque action de modification sur les attributions de rôles aux utilisateurs. Elle utilise un champ `JSONField` (`snap_infos`) pour stocker les infos au moment de la transaction et des FK pour permettre la recherche / filtre plus facilement.                        |

### Contexte des permissions <a id="permissions-context"></a>

Une permission s'applique dans un contexte particulier. Cinq (6) contextes sont définis: système (`SYSTEM`), délégation (`DELEGATE`), compagnie (`COMPANY`), multi-compagnies (`MULTI_COMPANIES`), location (`LOCATION`) et multi-location (`MULTI_LOCATIONS`).

#### Système (`access_permission.context = SYSTEM`)

La permission concerne une configuration externe aux compagnies (*ex: création d'utilisateur, téléversement d'images sur le serveur*)

#### Délégation (`access_permission.context = DELEGATE`)

La permission définit une permission / rôle spécial. Les permissions pouvant être déléguées doivent être précisées. Ces permissions sont enregistrées dans la table `access_roledelegatepermissions`. 

*Exemple: `access.role.manage` est assignée au rôle "Gestionnaire d'accès". Les permissions `inventory.stock.increase` et `inventory.stock.decrease` sont précisées comme délégables. Cela sgnifie qu'un Gestionnaire d'accès peut créer des rôles avec ces 2 permissions et seulement ces 2 permissions. Il ne peut,pas augmenter ou diminuer l'inventaire lui-même l'inventaire en stock avec cette permission.*

La permission s'applique exclusivement dans un contexte d'entreprise, sans info sur les locations.

#### Compagnie (`access_permission.context = COMPANY`)

La permission s'applique exclusivement dans un contexte d'entreprise active. Il n'y a pas d'information de location nécessaire.

*Exemples:  L'utilisateur authentifié a la permission `catalogue.product.add` valide pour l'Entreprise A seulement.*

- `.../c/entreprise-a/product/add` => Accès granted
- `.../c/entreprise-b/product/add` => Error Permission denied
-  `.../c/notexistslugcompany/product/add` => Error Permission denied
- `.../product/add` => Error Company Context Missing

#### Multi-compagnies (`access_permission.context = MULTI_COMPANIES`)

La permission concerne une demande d'aggrégation (rapport consolidé sur plusieurs compagnies). Il n'y a pas d'information de location nécessaire.

Quatre règles :
1. la permission autorise une fonctionnalité multi-compagnies ;
2. elle ne donne pas accès à toutes les compagnies ;
3. le périmètre vient des rôles et assignations ordinaires ;
4. toute compagnie demandée hors de ce périmètre provoque un refus complet 403.

#### Location (`access_permission.context = LOCATION`)

La permission s'applique exclusivement dans un contexte d'entreprise active ET pour une location en particulier.

*Exemple:  L'utilisateur authentifié a la permission `inventory.stock.view` valide pour `entreprise-a` à partir de la location `entrepôt-a` seulement. `etagere-r` est une location enfant de entrepot-a.*

- Voir le stock de `etagere-r` => Accès granted
- Voir le stock de la location `boutique-a` (pas un enfant de entrepôt-x) => Permission denied

#### Multi-locations (`access_permission.context = MULTI_LOCATIONS`)

La permission s'applique dans un contexte d'entreprise active (1 compagnie active) pour les locations listées.

*Exemple:  L'utilisateur authentifié a la permission `inventory.stock.relocate` valide pour `entreprise-a` à partir de la location `entrepôt-x` seulement. `product-1` est un produit du catalogue de `entreprise-a`; `etagere-r` et `zone-emballage` sont des locations enfant de entrepot-x.*

- déplacer `product-1` de `etagere-r` à `zone-emballage` => Accès accordé

- déplacer `product-1` de `etagere-r` à `boutique-a` (pas un enfant de entrepôt-x) => Error Permission denied.
  
  - À noter que l'interface ne devrait pas proposer `boutique-a` mais si une manipulation malvellante était réalisée, le système refuserait le transfert.

- déplacer `product-2` situé dans `boutique-a` => Error Permission denied.

### Sensibilité des permissions <a id="permissions-sensibility"></a>

Le concept de sensibilité d'une permission pourrait permettre d'adapter l'UI et d'ajouter des confirmations d'assignation explicites.

| Sensibilité | Description                                                                                        |
| ----------- | -------------------------------------------------------------------------------------------------- |
| LOW         | La permissions est générale et a peu d'impact sur le stock ou le system.                           |
| MEDIUM      | La permission a un impact sur la configuration de l'entreprise et/ou la manière de gérer le stock. |
| HIGH        | La permission permet de faire des changements majeurs aux stocks                                   |

##### Sensibilité OWNER-ONLY

Il s'agit d'une permission qui n'est pas déléguable. Elle peut être réalisée exclusivement par un utilisateur avec `is_owner=True`.

#### Matrices de décision RBAC concernant les permissions

##### Partie 1 : Permissions de type "Compagnie & Lieu" (`context = COMPANY`)<a id="matriceRBAC"></a>

| `access_role .company_id` | `users_userrole .company_id` | `users_userrole .location_id` | Accès de l'utilisateur                                                                        |
| ------------------------- | ---------------------------- | ----------------------------- | --------------------------------------------------------------------------------------------- |
| **NULL**                  | **NULL**                     | **NULL**                      | **Accès total** : Toutes les compagnies et toutes les locations.                              |
| **NULL**                  | **X**                        | **NULL**                      | **Accès restreint** : Compagnie X seulement, sans restriction de location.                    |
| **NULL**                  | **X**                        | **A**                         | **Accès restreint** : Compagnie X seulement, et uniquement pour la location A et ses enfants. |
| **NULL**                  | **NULL**                     | **A**                         | **Incohérent / Refusé** : Un lieu ne peut pas être validé sans contexte de compagnie.         |
|                           |                              |                               |                                                                                               |
| **X**                     | **NULL**                     | **NULL**                      | **Accès restreint** : Compagnie X seulement, sans restriction de location.                    |
| **X**                     | **X**                        | **NULL**                      | **Accès restreint** : Compagnie X seulement, sans restriction de location.                    |
| **X**                     | **X**                        | **A**                         | **Accès restreint** : Compagnie X seulement, et uniquement pour la location A et ses enfants. |
| **X**                     | **NULL**                     | **A**                         | **Accès restreint** : Compagnie X seulement, et uniquement pour la location A et ses enfants. |
|                           |                              |                               |                                                                                               |
| **X**                     | **Y**                        | *Peu importe*                 | **Refusé** : La compagnie active ne peut pas être X et Y à la fois.                           |

1. Les lignes où `access_role.company_id = X` et `userrole.company_id = NULL` (ou vice-versa) fonctionnent comme un **entonnoir** : c'est la restriction la plus sévère qui l'emporte toujours.
2. Si un `userrole.location_id` est présent, la validation du lieu s'enclenche **uniquement** si la compagnie a d'avance été validée avec succès.

##### Partie 2 : Permissions de type "Global" (`need_globalcontext = True`)

| `access_role .company_id` | `users_userrole .company_id` | `users_userrole .location_id` | Accès de l'utilisateur                                                                                          |
| ------------------------- | ---------------------------- | ----------------------------- | --------------------------------------------------------------------------------------------------------------- |
| **NULL**                  | **NULL**                     | **NULL**                      | **Accès accordé** : L'action globale est autorisée car l'utilisateur a un rôle global (sans restriction).       |
| **NULL**                  | **X**                        | *Peu importe*                 | **Refusé** : L'action requiert un pouvoir global, mais l'utilisateur est restreint à la compagnie X.            |
| **NULL**                  | *Peu importe*                | **A**                         | **Refusé** : L'action requiert un pouvoir global, mais l'utilisateur est restreint au lieu A.                   |
| **X**                     | *Peu importe*                | *Peu importe*                 | **Refusé** : Configuration invalide (Une action globale ne peut pas être rattachée à une compagnie spécifique). |

---

### Vérification des permissions

Le système de permissions natif de Django est conçu pour être étendu et remplacé grâce à un mécanisme appelé **Authentication Backends**. Ainsi, la question des permissions du Custom RBAC peut être répondu avec `user.has_perm() avec, en coulisse, une résolution qui va vérifier les tables du Custom RBAC.

La question:

```text
Cet utilisateur peut-il effectuer cette action dans ce contexte et ce périmètre?
```

#### Arbre de décision

```text
[ Début ] ──> L'utilisateur est-il inactif ? ──[Oui]──> RETOURNER FAUX
                 │
                 └──[Non]──> Est-il Owner ? ──[Oui]──> RETOURNER VRAI (Bypass complet)
                                │
                                └──[Non]
                                     ▼
                     [ Validation du paramètre `obj` (Contexte) ]
                 Vérification des structures requises selon le type de permission
          (Déclenche un Warning ou lève une Exception / Invalidation immédiate)
                                     │
                                     ▼
                      [ Trouver la Permission demandée ]
                                     │
                                     ▼
          [ Filtrage & Boucle sur les Permissions assignées à l'utilisateur via UserRoles ]
    EXCLURE d'emblée les UserRoles inactifs, les Permissions inactives ou rattachées à un Rôle inactif.
                                     │
                                     ├── Aucune permission trouvée ──> RETOURNER FAUX
                                     ▼
          [ Boucle sur chaque Permission valide assignée à l'utilisateur ]
                                     │
                     Est-ce la permission recherchée ?
                                     │
                                     ├── [Non] ──> Passer à la suivante
                                     └── [Oui] ──> Comparaison du contexte requis par la permission avec le contexte (Obj) fourni
                                                       │
         ┌─────────────────────────────────────────────┼──────────────────────────────────────────────┐
         ▼                                             ▼                                              ▼
   [ Permission SYSTEM ]                [ Permission COMPANY / DELEGATE ]                [ Permission LOCATION / MULTI_LOCATIONS ]
   │  (si Obj est fourni, un                Obj matche-t-il ?                               La location (ou liste) matche-t-elle
   │   warning a déjà été préparé)               ├── Non ──> Passer au suivant                  l'assignation ou ses enfants ?
   └───> RETOURNER VRAI                          └── Oui ──> RETOURNER VRAI                     ├── Oui ──> RETOURNER VRAI
                                                                                                └── Non ──> Passer au suivant

         └────────────────────────────────────────────┬───────────────────────────────────────────────┘ 
                                                      ▼
                                            [ FIN DE LA BOUCLE  ]   
                                                      └───> RETOURNER FAUX                           
```

Validation du paramètre `obj` (Contexte)

```text
[ Paramètre `obj` reçu ] ──> Est-ce un Dictionnaire ?
                               │
                               ├── [Non] ──> Si la Perm nécessite un Contexte ──> LEVER EXCEPTION (Invalid Context)
                               └── [Oui]
                                    ▼
                     [ ÉVALUATION DU TYPE DE CONTEXTE ]
                                    │
    ┌───────────────────────────────┘                          
    ├── SYSTEM ─────────────────────> `company_id` OU `location_id` est fourni ?
    │                                    ├── [Oui] ──> ÉMETTRE WARNING : "SYSTEM permission ignores context"
    │                                    └─> CONTEXTE VALIDE
    │
    ├── DELEGATE ───────────────────> `company_id` est-il absent ? ──[Oui]──> LEVER EXCEPTION (Missing Company)
    │                                    │
    │                                    └──[Non] ──> Est-ce une liste/un array ? ──[Oui]──> LEVER EXCEPTION (Too Many Companies)
    │                                                   │
    │                                                   └──[Non] ──> `location_id` est-il fourni ?
    │                                                                   ├── [Oui] ──> ÉMETTRE WARNING : "Location ignored for DELEGATE context"
    │                                                                   └─> CONTEXTE VALIDE
    │
    ├── COMPANY ────────────────────> `company_id` est-il absent ? ──[Oui]──> LEVER EXCEPTION (Missing Company)
    │                                    │
    │                                    └──[Non] ──> Est-ce une liste/un array ? ──[Oui]──> LEVER EXCEPTION (Too Many Companies)
    │                                                   │
    │                                                   └──[Non] ──> `location_id` est-il fourni ?
    │                                                                   ├── [Oui] ──> ÉMETTRE WARNING : "Location ignored for COMPANY context"
    │                                                                                  └──> CONTEXTE VALIDE
    │
    ├── MULTI_COMPANIES ────────────> `company_id` est-il absent ? ──[Oui]──> LEVER EXCEPTION (Missing Company)
    │                                    │
    │                                    └──[Non] ──> `location_id` est-il fourni ?
    │                                                    ├── [Oui] ──> ÉMETTRE WARNING : "Location ignored for MULTI_COMPANIES context"
    │                                                                    └─> CONTEXTE VALIDE
    │
    ├── LOCATION ───────────────────> `company_id` absent OU est une liste ? ──[Oui]──> LEVER EXCEPTION (Single Company Required)
    │                                    │
    │                                    └──[Non] ──> `location_id` absent OU est une liste ? 
    │                                                   ├── [Oui] ──> LEVER EXCEPTION (Single Location Required)
    │                                                   └── [Non] ──> CONTEXTE VALIDE
    │
    └── MULTI_LOCATIONS ────────────> `company_id` absent OU est une liste ? ──[Oui]──> LEVER EXCEPTION (Single Company Required)
                                         │
                                         └──[Non] ──> `location_id` absent OU n'est pas une liste ? ──[Oui]──> LEVER EXCEPTION (Array Required)
                                                        │
                                                        └──[Oui, liste] ──> Nombre d'éléments < 2 ? 
                                                                               ├──[Oui] ──> LEVER EXCEPTION (At least 2 Locations required)
                                                                               └──[Non] ──> CONTEXTE VALIDE
```

#### Backend d'Authentification personnalisé <a id="auth-backend"></a>

```python
# django-stock/src/access/auth_backend.py

from django.db.models import Prefetch
from django.core.exceptions import ObjectDoesNotExist
# Importez les modèles (UserRole, AccessPermission, AccessRole, AccessRolePermission, Company, Location.)

class CompanyRBACBackend:
    """
    Backend de permission personnalisé pour gérer le RBAC par Compagnie et Lieu.
    Est optimisé pour minimiser les requêtes à la base de données.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # On ne gère pas l'authentification (login) dans ce backend, 
        # on retourne None pour laisser les autres backends s'en charger.
        return None

    def has_perm(self, user_obj, perm, obj=None):
        """
        Surcharge la vérification des permissions.
        :param user_obj: L'instance de l'utilisateur connecté.
        :param perm: Le codename string de la permission (ex: 'catalogue.product.delete').
        :param obj: Un dictionnaire optionnel contenant le contexte à vérifier 
           SYSTEM          - None
           DELEGATECOMPANY - { "company_id": A }
           LOCATION        - { "company_id": A, "location_id": Y }
           MULTI_LOCATIONS - { "company_id": A, "location_id": [Y, X] }
           MULTI_COMPANIES - { "company_id": [A, B] }
        """
        ...                 
```

##### Enregistrer le Backend dans `settings.py`

```python
# django-stock/src/config/settings.py

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend', # Le backend par défaut de Django
    'src.access.auth_backend.CompanyRBACBackend', # Votre nouveau backend
]
```

##### Dernière étape d'optimisation de CompanyRBACBackend: cache applicatif

Si la méthode consomme encore trop de ressources lors de pics de charge, l'étape ultime consisterait à mettre le résultat de cette fonction dans le **Cache de Django** (`django.core.cache`) avec une clé unique basée sur l'utilisateur et le contexte :

```python
f"rbac_{user.id}_{permission_codename}_{context_company_id}_{context_location_id}"
```

Il faudra penser à supprimer cette clé de cache à chaque fois qu'un objet de la table `UserRole` est modifié ou supprimé (via un signal Django `post_save` / `post_delete`).

##### Application dans les Vues Django :

```python
# Exemple 1 : Vérification d'une action globale
# Pas besoin de passer de contexte
if user.has_perm('core.settings.change'):
    print("Accès accordé au panneau global !")

# Exemple 2 : Vérification d'une action métier (need_companycontext=True) :
contexte = {
    "company_id": current_company.id, 
    "location_id": current_location.id
}

if user.has_perm('catalogue.product.delete', obj=contexte):
    print("L'utilisateur a le droit de supprimer le produit appartenant à cette compagnie.")
else:
    raise PermissionDenied()
```

Ou, encore mieux, créer un décorateur de vue personnalisé, dans un mixin.

###### Mixin

```python
# django-stock/access/mixins.py

from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied

class RBACRequiredMixin(AccessMixin):
    """
    Mixin pour les Class-Based Views de Django.
    Vérifie si l'utilisateur possède la permission RBAC requise.
    """
    # Attribut à définir obligatoirement dans vos vues
    permission_codename = None 

    def dispatch(self, request, *args, **kwargs):
        # 1. Sécurité de développement : s'assurer que le développeur a configuré le codename
        if self.permission_codename is None:
            raise NotImplementedError(
                f"{self.__class__.__name__} requiert la définition de l'attribut 'permission_codename'."
            )

        # 2. Vérifier si l'utilisateur est connecté et actif
        if not request.user.is_authenticated or not request.user.is_active:
            return self.handle_no_permission()

        # 3. Appel de la méthode user.has_perm native (qui utilise le backend personnalisé)
        # Le CompanyContext est déjà alimenté par le CompanyMiddleware à ce stade de la requête.
        if not request.user.has_perm(self.permission_codename):
            raise PermissionDenied("Vous n'avez pas les droits nécessaires pour accéder à cette ressource.")

        # 4. Si tout est valide, on laisse Django continuer le cycle normal de la vue (dispatch)
        return super().dispatch(request, *args, **kwargs)
```

###### Utilisation

```python
# django-stock/catalogue/views.py

from django.views.generic import DeleteView
from django.urls import reverse_lazy
from src.access.mixins import RBACRequiredMixin
from .models import Product

class ProductDeleteView(RBACRequiredMixin, DeleteView):
    model = Product
    template_name = 'catalogue/product_confirm_delete.html'
    success_url = reverse_lazy('product_list')

    # LA ligne magique : le mixin s'occupe de tout le reste !
    permission_codename = 'catalogue.product.delete'

    def get_object(self, queryset=None):
        """
        Le CompanyScopedManager filtre déjà les produits de la compagnie courante.
        On récupère l'objet de manière sécurisée.
        """
        return super().get_object(queryset)
```

---

## Référentiel des permissions <a id="permissions"></a>

Les permissions sont créées lors de la configuration initiale de l'application.

Les permissions suivent le modèle suivant: *[app_name].[model_name].[OPT][perm_type]*.

- *perm_type* reprend les CRUD officiels de django (`view`, `add`, `change`, delete`) `et les étend en les regroupant parfois (ex: `manage`) ou en ciblant un champs spécifique et/ou la valeur permise (ex: `setactivate`dans `users.user.setactivate`  permet de modifier le field `is_active `de l'utilisateur)
- *model_name* est parfois sauté car la permission concerne plusieurs tables (ex: `access.manage` permet de faire des changements dans les tables `access_role `et `access_rolepermissions`)
- *OPT* est optionnel et est utilisé pour quelques permissions (ex: `company.location.main.add` et `company.location.sub.add` permettent respectivement de créer des emplacements de haut niveau (location racine, sans aucun parent)  et des emplacements de sous-location (location enfant)

> [!TIP]
> *Les fonctionnalités sous-jacentes à chaque permission seront implémentées à différents stades du développement. Certaines permissions sont projetées mais pourraient être codé différemment selon l'évolution du produit et de l'UX.*

### Légende et explications

#### Contexte

Une permission peut être `SYSTEM`, `COMPANY`, `MULTI_COMPANIES`, `LOCATION `ou `MULTI_LOCATIONS`. Voir section [RBAC Custom - Contexte des permissions](#permissions-context)

#### Sensibilité

Voir section [RBAC Custom - Sensibilité des permissions](#permissions-sensibility)

#### Permission barrée

Cette permission ne sera **PAS** créée car

1. elle est bloquée / impossible pour tous les utilisateurs métier OU
2. elle est listée /  groupée sous un autre nom OU
3. elle est "OWNER-ONLY"

La permission est listée malgré tout dans le référentiel à des fins de documentation.

### 5.1. ![](https://img.shields.io/badge/-App-darkblue.svg) Core (`core.*`)

Centralise les configurations globales du système.

| Code (`codename`)          | Description (`name` / `help_text`)                                                                  | Contexte | Sensibilité |
|:-------------------------- |:--------------------------------------------------------------------------------------------------- |:--------:|:-----------:|
| ~~`core.settings.add`~~    | Ajouter une configuration globale.*La table core.settings ne contient qu'un seul enregistrement.*   | -        | -           |
| ~~`core.settings.view`~~   | Consulter les configurations globales                                                               | -        | OWNER-ONLY  |
| ~~`core.settings.change`~~ | Modifier les configurations globales                                                                | -        | OWNER-ONLY  |
| ~~`core.settings.delete`~~ | Supprimer les configuration globales.*La table core.settings doit contenir un seul enregistrement.* | -        | -           |
| ~~`core.image.[view        | add                                                                                                 | change   | delete]`~~  |

### 5.2. ![](https://img.shields.io/badge/-App-darkblue.svg) Access (`access.*`)

Configure les rôles de l'application

| Code (`codename`)            | Description (`name` / `help_text`)                                                                                                                                                                 | Contexte   | Sensibilité                                                                                                                                                                           |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |:----------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| ~~`access.permission.[add    | change                                                                                                                                                                                             | delete]`~~ | Changer les  informations de la table des permissions.*Impossible car chaque permission est associée à un comportement d'accessibilité codé en dur. Cette table est en lecture seule* |
| ~~`access.permission.view`~~ | Voir les informations de la table des permissions.* Non créé explicitement car pas de besoins. *                                                                                                   | -          | -                                                                                                                                                                                     |
| ~~`access.role.[view         | add                                                                                                                                                                                                | change     | delete]`~~ et ~~`access.rolepermissions.[view                                                                                                                                         |
| `access.role.manage`         | *Gérer les rôles et leur association avec des permissions.<br/><br/>Cette permission est strictement encadrée pour empêcher l'escalade de privilèges. Voir la [section dédiée](#rolemanage).*<br/> | DELEGATE   | HIGH                                                                                                                                                                                  |

#### Limites et encadrement de `access.role.manage`<a id="rolemanage"></a>

##### Cas propriétaire

Un propriétaire n'a pas besoin de la permission `access.role.manage`: il a accès sans restriction à la gestion des rôles et de leurs permissions.

* Il peut définir un rôle global (avec `company_id = NULL`) ou un rôle limité à une compagnie (`company_id`est renseigné).
* Il peut assigner n'importe quelle permission à un rôle.
* Il peut assigner des rôles à des employés.

###### Règles entourant la création d'un rôle qui contient `access.role.manage`

Un rôle qui contient la permission `access.role.manage` doit respecter des règles précises:

1. Le rôle ne peut pas être global. La company doit toujours être renseignée. Le système refusera de créer un rôle global qui contient `access.role.manage`.
2. Les autres permissions du rôle ne sont pas des permissions normales d'employés: elles **représentent la liste des permissions manipulables** par l'employé qui recevra le rôle. Elles ne donnent pas le droit de réaliser l'action même.
3. La liste des permissions accompagnant `access.role.manage` s'applique exclusivement à la compagnie précisée.

```text
Exemple :
* rôle particulier A, compagnie X : access.role.manage + catalogue.product.view
* rôle particulier B, compagnie Y : access.role.manage + inventory.stock.adjust
Alice ne doit pas pouvoir créer dans X un rôle contenant inventory.stock.adjust.
```

1. La liste des permissions accompagnant `access.role.manage` s'applique exclusivement à la compagnie précisée.###### Règles entourant l'assignation d'un rôle qui contient`access.role.manage`

Le propriétaire peut déléguer la responsabilité de créer des rôles à un employé mais cette assignation doit répondre à deux règles:

1. `users_userrole.company_id` doit être défini sur la même compagnie que le rôle (`access_role.company_id`). Il s'agit d'une validation supplémentaire de la volonté du propriétaire

2. `location_id `doit être NULL.
   
   1. Un rôle ne peut pas être limité à une location donc la création de nouveaux rôles ne peut pas l'être non plus.

##### Cas employé assigné à la permission `access.role.manage`

Un employé ayant reçu la permission `access.role.manage` est strictement limité dans la vue, la création, la mise à jour et la suppression des rôles qu'il peut gérer.

1. Il ne voit que les rôles qu'il a lui-même créés (`access_role.created_by_id` le représente). Il ne peut mettre à jour ou supprimer que ces rôles.
2. Les rôles créés ou mis à jour sont toujours limités à une entreprise précise. Ainsi:   `access_role.company_id` du rôle géré = `company_id` du rôle ou des rôles contenant `access.role.manage`.
3. Les permissions qu'il a le droit d'assigner dans ses rôles sont un sous-groupe de la liste complète des permissions. Ce sous-groupe est défini par la liste des permissions du rôle contenant `access.role.manage`.
4. La permission `access.role.manage` n'est jamais assignable.

##### Résumé

- `access.role.manage` est une capacité de délégation.
- Les autres permissions du même rôle ne sont pas accordées à son détenteur.
- Elles définissent uniquement le sous-ensemble de permissions qu’il peut placer dans les rôles qu’il crée.
- Les rôles contenant `access.role.manage` sont exclus de l’évaluation normale des permissions.
- Le rôle particulier est limité à une compagnie.
- L’assignation est limitée à cette même compagnie et ne peut pas avoir de `location_id`.

---

### 5.3. ![](https://img.shields.io/badge/-App-darkblue.svg) Users (`users.*`)

Gère les profils utilisateurs et leurs accès.

**Relation hiérarchique entre employés**: Un employé a accès uniquement à tous ses subordonnées (arbre hiérarchique défini par la table users_userhierarchy, un modèle qui utilse MP_Node de django-treebeard)

**Prévention de l'escalade de privilèges**: en tout temps, les permissions pouvant être assignées sont strictement limitées aux permissions détenues par l'utilisateur qui fait l'assignation, sans jamais dépassé son propre périmètre (les `company_id `et `location_id `de ses propres rôles). Un utilisateur ne peut en aucun temps modifier ses propres permissions.

| Code (`codename`)                                                                        | Description (`name` / `help_text`)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | Contexte   | Sensibilité                                                                                                  |
|:---------------------------------------------------------------------------------------- |:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |:----------:|:------------------------------------------------------------------------------------------------------------:|
| `users.user.add`                                                                         | Créer un nouvel utilisateur dans le système.<br/> - Le champs `is_owner `est invisible, bloqué et fixé à `False `en tout temps pour un utilisateur qui n'est pas `is_owner=True`.<br/>- L'utilisateur créé sera un subordonné de l'utilisateur "créateur"                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | SYSTEM     | LOW                                                                                                          |
| `users.user.invite`                                                                      | Inviter un utilisateur à créer son propre compte à partir d'un courriel contenant un lien sécurisé                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | SYSTEM     | LOW                                                                                                          |
| `users.user.view`                                                                        | Voir la liste des utilisateurs, incluant leur secteur d'activité<br/><br/>*Un utilisateur avec cette permission ne voit que ses subordonnés.*                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | SYSTEM     | LOW                                                                                                          |
| `users.user.change`                                                                      | Modifier les informations ou préférences d'un utilisateur, excluant le drapeau propriétaire (`user.is_owner`) et incluant leur secteur d'activité<br/><br/>*Un utilisateur avec cette permission ne peut modifier que ses subordonnés.*                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | SYSTEM     | LOW                                                                                                          |
| ~~`users.user.setowner`~~                                                                | Modifier la valeur du champ user.is_owner.*Cette action n'est pas déléguable.*<br/><br/>- Un propriétaire ne peut jamais se révoquer (set `is_owner=false`) lui-même.<br/>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | SYSTEM     | OWNER-ONLY                                                                                                   |
| `users.user.change_own`                                                                  | Modifier les informations et préférences de son propre profil<br/>- Exclut la modification de`user.is_owner`, qui n'est d'ailleurs visible que pour les propriétaires.<br/>- Exclut la modification du superviseur (mais l'info sur le superviseur direct est affiché)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | SYSTEM     | LOW                                                                                                          |
| `users.user.delete`                                                                      | Supprimer un utilisateur (le système refusera si<br/>- il existe au moins une référence à cet utilisateur<br/>- cet utilisteur est `is_owner=True`)<br/><br/>*Un utilisateur avec cette permission ne peut supprimer le compte que de ses subordonnés.*                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | SYSTEM     | MEDIUM                                                                                                       |
| `users.user.setactivation`                                                               | Activer ou désactiver le compte d'un utilisateur (set`user.is_active`)<br/>Cette permission sert à permettre l'activation/désactivation d'un compte sans donner le contrôle total `users.user.change`<br/>*Un utilisateur avec cette permission ne peut changer le statut d'activation que de ses subordonnés.*                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | SYSTEM     | LOW                                                                                                          |
| ~~`users.useractivitysector.view`~~                                                      | Voir les secteurs d'activité.<br/>*Cette permission est incluse dans `users.user.view`*                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |            |                                                                                                              |
| ~~`users.useractivitysector.[<br/>add                                                    | change                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | delete]`~~ | Gérer les secteurs d'activités des utilisateurs<br/>*Ces permissions sont incluses dans `users.user.change`* |
| ~~`users.userrole.add`~~<br/>~~`users.userrole.change`~~<br/>~~`users.userrole.delete`~~ | Assigner, modifier ou supprimer les rôles d'un utilisateur. Regroupement sous une seule permission`users.userrole.manage`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | -          | -                                                                                                            |
| `users.userrole.view`                                                                    | Consulter les rôles assignés à une liste d'utilisateurs.<br/><br/>*Un utilisateur avec cette permission ne peut voir les permissions que de ses subordonnés.*                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | SYSTEM     | MEDIUM                                                                                                       |
| `users.userrole.manage`                                                                  | Assigner, modifier ou supprimer les rôles assignés à un utilisateur.<br/><br/>*L'utilisateur avec cette permission est strictement limité <br/>1. Un utilisateur avec cette permission ne peut modifier les permissions que de ses subordonnés. <br/>2. Les permissions pouvant être assignées sont strictement limitées aux permissions détenues par l'utilisateur ayant cette permission (prévention de l'escalade des privilèges).<br/>3. En tout temps, il est interdit pour l'utilisateur de s'auto-assigner des permission.*<br/><br/>L'interface est filtrée pour éviter les erreurs de permissions. Ceci dit, avant l'enregistrement des permissions en DB, les règles sont revérifiées et une erreur de validation est lancée et loguée dans userrolelog si non respectée. Le changement en DB est évidemment non effectué. | SYSTEM     | HIGH                                                                                                         |
| users.userrolelog.view                                                                   | Voir l'historique des modifications sur les assignations de rôle.<br/><br/>*Un utilisateur avec cette permission ne peut voir les informations  concernant que ses subordonnés.*                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | SYSTEM     | MEDIUM                                                                                                       |
| ~~`users.userrolelog.[add                                                                | change                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | delete]`~~ | `userrolelog `est en lecture seule pour tous (incluant `is_owner=True`)                                      |

### 5.4. ![](https://img.shields.io/badge/-App-darkblue.svg) Company (`company.*`)

Application permettant de configurer les entreprises, leurs unités de mesure et leurs emplacements [détails ⬀](5-django-apps-and-urls.md#company).

| Code (`codename`)             | Description (`name` / `help_text`)                                                                                                                                                                                                                                                                                                        | Contexte   | Sensibilité                                                                                                                                                             |
|:----------------------------- |:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |:----------:|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| `company.company.view`        | Voir les informations de configuration de l'entreprise.                                                                                                                                                                                                                                                                                   | COMPANY    | MEDIUM                                                                                                                                                                  |
| ~~`company.company.add`~~     | Créer une nouvelle entreprise. Cette action n'est pas déléguable.                                                                                                                                                                                                                                                                         | SYSTEM     | OWNER-ONLY                                                                                                                                                              |
| ~~`company.company.change`~~  | Modifier les informations de l'entreprise. Cette action n'est pas déléguable.                                                                                                                                                                                                                                                             | COMPANY    | OWNER-ONLY                                                                                                                                                              |
| ~~`company.company.archive`~~ | Archiver ou désarchiver l'entreprise<br/>Une entreprise archivée `(is_archive = True`) n'est plus disponible pour aucune action (création de produit, modification d'inventaire, etc) et n'apparaît plus dans le tableau de bord et les rapports consolidés [Est en consultation seulement]. <br/><br/>Cette action n'est pas déléguable. | COMPANY    | OWNER-ONLY                                                                                                                                                              |
| ~~`company.company.delete`~~  | Supprimer une entreprise.  Cette action est irréversible et supprime l'entreprise, toutes les références et tout l'historique associé à l'entreprise. Tous les rôles associés à l'entreprises et toutes les assignations de rôle limitées à cette entreprise sont également supprimées.<br/><br/>Cette action n'est pas déléguable.       | COMPANY    | OWNER-ONLY                                                                                                                                                              |
| ~~`company.locationtype.[view | add                                                                                                                                                                                                                                                                                                                                       | change     | delete]`~~                                                                                                                                                              |
| `company.locationtype.manage` | Gérer les types de location (voir, ajouter, modifier et supprimer)                                                                                                                                                                                                                                                                        | COMPANY    | MEDIUM                                                                                                                                                                  |
| `company.location.view`       | Consulter les emplacements                                                                                                                                                                                                                                                                                                                | COMPANY    | LOW                                                                                                                                                                     |
| ~~`company.location.main.[add | change                                                                                                                                                                                                                                                                                                                                    | delete]`~~ | Créer, modifier ou supprimer un emplacement de haut niveau (emplacement racine)<br/><br/>Cette action n'est pas déléguable.                                             |
| ~~company.location.sub.view~~ | Géré par company.location.view (sans distinction entre "main" ou "sub")                                                                                                                                                                                                                                                                   | -          | -                                                                                                                                                                       |
| ~~`company.location.sub.[add  | change                                                                                                                                                                                                                                                                                                                                    | delete]`~~ | Créer, modifier ou supprimer un sous-emplacement (emplacement qui a nécessairement un parent)<br/><br/>Actions regroupées sous le libellé `company.location.sub.manage` |
| `company.location.sub.manage` | Gérer les sous-locations (emplacements enfants). À la création / mise à jour, le système doit vérifier que le parent choisi appartient bien à la même entreprise. Aussi, le système empêchera la suppression si des références (stock) y font référence.                                                                                  | COMPANY    | MEDIUM                                                                                                                                                                  |
| `company.uom.view`            | Consulter toutes les unités de mesure définies dans l'entreprise                                                                                                                                                                                                                                                                          | COMPANY    | LOW                                                                                                                                                                     |
| `company.uom.manage`          | Gérer toutes les unités de mesure utilisées dans l'entreprise.                                                                                                                                                                                                                                                                            | COMPANY    | HIGH                                                                                                                                                                    |
| ~~company.import~~            | Importer massivement les données d'une entreprise, incluant les infos de locations, le catalogue et l'inventaire (CSV).<br/><br/>Le système ajoute les données aux données déjà existantes. Habituellement fait sur une entreprise nouvelle créée.                                                                                        | COMPANY    | OWNER-ONLY                                                                                                                                                              |
| ~~company.export~~            | Exporter les données d'une entreprise, incluant les infos de locations, le catalogue et l'inventaire (CSV).                                                                                                                                                                                                                               | COMPANY    | OWNER-ONLY                                                                                                                                                              |

### 5.5. ![](https://img.shields.io/badge/-App-darkblue.svg) Catalogue (`catalogue.*`)

Application gérant le référentiel des produits, leurs déclinaisons (variantes), leur classification (catégories), leurs images, leur conditionnement (packaging) et leurs caractéristiques techniques [détails ⬀](5-django-apps-and-urls.md#catalogue).

| Code (`codename`)                                                 | Description (`name` / `help_text`)                                                                                                                                                                                                                                                                                                            | Contexte   | Sensibilité                                                                                 |
|:----------------------------------------------------------------- |:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |:----------:|:-------------------------------------------------------------------------------------------:|
| `catalogue.product.view`                                          | Consulter le catalogue des produits (inclut les infos des modèles de produit, leurs variantes. leurs catégories, leurs images associées et leur conditionnement. Exlut les infos de configuration).                                                                                                                                           | COMPANY    | LOW                                                                                         |
| `catalogue.product.add`                                           | Créer un nouveau produit (inclut les modèles de produit, leurs variantes. leurs catégories, leurs images associées et leur conditionnement. Exclut l'archivage.                                                                                                                                                                               | COMPANY    | MEDIUM                                                                                      |
| `catalogue.product.change`                                        | Modifier les caractéristiques d'une  fiche produit (inclut les modèles de produit, leurs variantes. leurs catégories, leurs images associées et leur conditionnement. Exclut l'archivage.                                                                                                                                                     | COMPANY    | MEDIUM                                                                                      |
| `catalogue.product.imagesupload`                                  | Téléverser des images sur le serveur en lien avec le produit. Avoir cette permission n'est utile qu'en association avec la permission de modifier un produit.                                                                                                                                                                                 | COMPANY    | MEDIUM                                                                                      |
| `catalogue.product.archive`                                       | Archiver ou désarchiver un produit.<br/>- Un produit archivé n'apparaît plus dans les listes de produits ni dans les recherches<br/>- *Un modèle archivé va archiver toutes ses variantes. Une variante archivée n'affecte pas son modèle ni les autres variante.* <br/>- Le système bloquera l'archivage si du stock existe pour ce produit. | COMPANY    | HIGH                                                                                        |
| `catalogue.product.delete`                                        | Supprimer définitivement un produit du catalogue de l'entreprise.*Le système bloquera la suppression si des référence au produit existe.*                                                                                                                                                                                                     | COMPANY    | HIGH                                                                                        |
| `catalogue.category.view`                                         | Consulter l'arborescence complète des catégories.                                                                                                                                                                                                                                                                                             | COMPANY    | LOW                                                                                         |
| ~~`catalogue.category.[add                                        | change                                                                                                                                                                                                                                                                                                                                        | delete]`~~ | Ajouter, modifier ou supprimer une catégorie.<br/><br/>Géré par `catalogue.category.manage` |
| `catalogue.category.manage`                                       | Gérer les catégories. Le système bloquera la suppression d'une catégorie référencée.                                                                                                                                                                                                                                                          | COMPANY    | MEDIUM                                                                                      |
| `catalogue.attribute.manage`                                      | Gérer les attributs (clé et valeurs) de variantes de produit dans un module dédié aux attributs, indépendemment des produits et leur assignation aux-dits attributs                                                                                                                                                                           | COMPANY    | HIGH                                                                                        |
| ~~view\|add\|create\|delete direct sur les modèles de catalogue~~ | Toutes les autres permissions CRUD directes sur les modèles (`ProducModel`, `ProductConfig`, `ProductPackaging`, `ProductAttribute`, `ProducImage`, `ProductModelImage`) sont gérées avec les permissions sur `Product`: un utilisateur ayant le droit de modifier un produit peut modifier toutes ses caractéristiques.                      | -          | -                                                                                           |

### 5.6. ![](https://img.shields.io/badge/-App-darkblue.svg) Inventory (`inventory.*`)

Application gérant l'état des stocks physiques, la traçabilité des lots et l'historique complet des mouvements de marchandises.

| Code (`codename`)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Description (`name` / `help_text`)                                                                                                                                                                                                              | Contexte        | Sensibilité                                                                                                                                                                                                     |
|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |:---------------:|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| `inventory.stock.view`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | Consulter les quantité   de stock disponibles.                                                                                                                                                                                                  | LOCATION        | MEDIUM                                                                                                                                                                                                          |
| ~~`inventory.stock.[add                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | change                                                                                                                                                                                                                                          | delete]`~~      | Ajouter/modifier/supprimer du stock en inventaire.<br/><br/>Actions impossible de cette manière: les permissions sont plus pointues et permettent de préciser la manière et les raisons pour modifier le stock. |
| `inventory.movement.view`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Consulter le journal historique des mouvements de stock. Permet de rechercher et filter.                                                                                                                                                        | COMPANY         | LOW                                                                                                                                                                                                             |
| ~~`inventory.movement.[add                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | change                                                                                                                                                                                                                                          | delete]`~~      | Actions impossibles car il s'agit d'un journal d'historique en lecture seule (même pour`is_owner=True`)                                                                                                         |
| ~~`inventory.movementreason.[view                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | add                                                                                                                                                                                                                                             | change          | delete]`~~                                                                                                                                                                                                      |
| `inventory.movementreason.manage`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Gérer les raisons pour modifier les quantités en inventaire. Permet d'associer la permission requise à la raison.                                                                                                                               | COMPANY         | HIGH                                                                                                                                                                                                            |
| <a id="permissions-reasons"></a>`inventory.stock.increase`<br/>`inventory.stock.decrease`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Augmenter ou diminuer l'inventaire (permissions génériques)<br/><br/>Cette permission générique est créée par flexibilité avec le système de movementreason personnalisé, au cas où aucune des autres permissions plus précise de conviendrait. | LOCATION        | HIGH                                                                                                                                                                                                            |
| `inventory.stock.purchase`<br/>*Ex: T-Shirt d'un fournisseur est reçu dans la zone de réception de marchandises.*<br/>*- stock.quantity est augmenté*<br/>*- un movement est créé avec location_source NULL et location_dest qui pointe vers la location modifiée.*                                                                                                                                                                                                                                                                                                                                                                                                                   | Augmenter l'inventaire en raison d'une commande d'achat à un fournisseur.                                                                                                                                                                       | LOCATION        | MEDIUM                                                                                                                                                                                                          |
| `inventory.stock.manufacture`<br/>*Ex: T-Shirt sort de la fabrique et est stocké dans l'entrepôt.*<br/>*- stock.quantity est augmenté*<br/>*- un movement est créé avec location_source NULL et location_dest qui pointe vers la location modifiée.                                                                                                                                                                                                                                                                                                                                                                                                                                   | Augmenter l'inventaire en raison de l'arrivée de produits issues d'une chaîne de production interne.                                                                                                                                            | LOCATION        | MEDIUM                                                                                                                                                                                                          |
| `inventory.stock.sale`<br/>*Ex: T-Shirt est vendu.*<br/>*- stock.quantity est diminué*<br/>*- un movement est créé avec location_source pointant vers la location modifié et location_dest NULL.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Diminuer l'inventaire en raison d'une vente.                                                                                                                                                                                                    | LOCATION        | MEDIUM                                                                                                                                                                                                          |
| `inventory.stock.count_more`<br/>*Ex: Le nombre de T-Shirt sur l'étagère A est plus élevé que la quantité indiquée en inventaire.*<br/>*- stock.quantity est augmenté*<br/>*- un movement est créé avec location_source et location_dest pointant vers la location modifiée.*                                                                                                                                                                                                                                                                                                                                                                                                         | Augmenter l'inventaire en raison d'un ajustement de décompte d'inventaire.                                                                                                                                                                      | LOCATION        | MEDIUM                                                                                                                                                                                                          |
| `inventory.stock.count_less`<br/>*Ex: Le nombre de T-Shirt sur l'étagère B est plus basse que la quantité indiquée en inventaire.*<br/>*- stock.quantity est diminué*<br/>*- un movement est créé avec location_source et location_dest pointant vers la location modifiée.*                                                                                                                                                                                                                                                                                                                                                                                                          | Diminuer l'inventaire en raison d'un ajustement de décompte d'inventaire.                                                                                                                                                                       | LOCATION        | MEDIUM                                                                                                                                                                                                          |
| `inventory.stock.loss`<br/>*Ex: Un T-Shirt sur l'étagère C est déchiré et donc retiré du stock courant.*<br/>*- stock.quantity est diminué*<br/>*- un movement est créé avec location_source pointant vers la location modifié et location_dest est NULL.*                                                                                                                                                                                                                                                                                                                                                                                                                            | Diminuer l'inventaire en raison de marchandises perdues (bris, vol, date de péremption dépassé, etc).                                                                                                                                           | LOCATION        | MEDIUM                                                                                                                                                                                                          |
| `inventory.stock.uom_pack`<br/>*Ex: 10 T-Shirt sont retirés de la tablette et placer dans une boîte pour une vente par pack plutôt que unitaire.*<br/>*- stock.quantity avec uom unit unit est diminué* <br/>*- stock.quantity avec uom unit pack est augmenté* <br/>*- un movement est créé avec location_source du premier changement et location_dest du deuxième changement. quantity_delta est 0.*                                                                                                                                                                                                                                                                               | Diminuer l'inventaire en raison d'un changement d'unité de mesure.                                                                                                                                                                              | LOCATION        | MEDIUM                                                                                                                                                                                                          |
| `inventory.stock.uom_unpack`<br/>*Ex: 10 T-Shirt sont retirés d'une boîte de fournisseur et placer sur la tablette pour renflouer l'emplacement.*<br/>*- stock.quantity avec uom unit parck est augmenté* <br/>*- stock.quantity avec uom unit unit est diminué* <br/>*- un movement est créé avec location_source du premier changement et location_dest du deuxième changement. quantity_delta est 0.*                                                                                                                                                                                                                                                                              | Augmenter l'inventaire en raison d'un changement d'unité de mesure.                                                                                                                                                                             | LOCATION        | MEDIUM                                                                                                                                                                                                          |
| `inventory.stock.relocate`<br/>*Ex: 1 T-Shirt est déplacé de l'emplacement Tablette A et placé dans l'emplacement  Lift 12.*<br/>*- stock.quantity de Tablette A est diminué* <br/>*- stock.quantity de Lift 12 est augmenté* <br/>*- un movement est créé avec location_source du premier changement et location_dest du deuxième changement. quantity_delta est 0.*                                                                                                                                                                                                                                                                                                                 | Diminuer l'inventaire pour le relocaliser dans un emplacement ayant le même parent principal.                                                                                                                                                   | MULTI_LOCATIONS | MEDIUM                                                                                                                                                                                                          |
| `inventory.stock.transfer_out`<br/>*Ex: 10 T-Shirt sont retirés de l'emplacement Zone Emballage de l'Entrepôt X pour être envoyés à Boutique ABC. Boutique ABC et Entrepôt X sont deux emplacements de haut niveau de la même entreprise. <br/>- Dans stock: qty est diminué de 10.<br/>- Dans movement: nouvelle entrée avec location_source pointant vers la Zone d'emballage de Entrepôt X et location_destination est NULL<br/>- Dans transit: nouvelle entrée avec les mêmes company_id (source et dest) et uom_id (source et dest). location_source_id pointe vers Entrepôt X, location_dest_id pointe vers Boutique ABC, quantity_received est NULL et is_complete est False.* | Diminuer l'inventaire pour l'envoyer dans un emplacement ayant un parent principal différent                                                                                                                                                    | LOCATION        | MEDIUM                                                                                                                                                                                                          |
| `inventory.stock.transfer_in`<br/>*Ex: 10 T-Shirt sont réceptionnés à Boutique ABC à partir du transit barcode (ou en sélectionnant la ligne du produit après avoir ouvert transit. <br/><br/>- Dans transit: entrée est mise à jour avec info du destinataire et, qté reçue et est marqué comme complété.* <br/>- Dans stock: qty est augmenté de 10.<br/>- Dans movement: nouvelle entrée avec location_source NULL et location_destination pointe vers Boutique ABC<br/>                                                                                                                                                                                                           | Augmenter l'inventaire pour l'envoyer dans un emplacement ayant un parent principal différent                                                                                                                                                   | LOCATION        | MEDIUM                                                                                                                                                                                                          |
| `inventory.stock.intercompany_out`<br/>*Ex: 10 T-Shirt sont retirés de l'emplacement Zone Emballage de l'Entrepôt X pour être envoyés à Entreprise Z. Entrepôt X et Entreprise Z sont deux entreprises indépendantes appartenant au même propriétaire <br/>- Dans stock: qty est diminué de 10.<br/>- Dans movement: nouvelle entrée avec location_source pointant vers la Zone d'emballage de Entrepôt X et location_destination est NULL<br/>- Dans transit: nouvelle entrée avec les infos de source et company_dest pointant vers Entreprise Z. location_dest, uom_dest et quantity_received sont NULL. is_complete est False.*                                                   | Diminuer l'inventaire en raison d'une vente interne vers une entreprise du même propriétaire.                                                                                                                                                   | LOCATION        | MEDIUM                                                                                                                                                                                                          |
| `inventory.stock.intercompany_in`<br/>*Ex: 10 T-Shirt sont réceptionnés à Entrepôt X à partir du transit barcode (ou en sélectionnant la ligne du produit après avoir ouvert la liste des transit. <br/>Dans transit: qté reçue et uom_dest sont mis à jour et is_completed est passé à True.* <br/>*- Dans stock: qty est augmenté de 10.*<br/>*- Dans movement: nouvelle entrée avec location_source NULL et location_destination pointe vers Entrepôt X (ou un emplacement interne d'Entrepôt X)*                                                                                                                                                                                  | Augmenter l'inventaire en raison de l'achat (la réception) interne de stock d'une entreprise du même propriétaire.                                                                                                                              | LOCATION        | MEDIUM                                                                                                                                                                                                          |

### 5.7. ![](https://img.shields.io/badge/-App-darkblue.svg) Reporting (`reporting.*`)

Pilote l'accès aux rapports et graphiques, par entreprise et globaux.

Exemple de rapports qui pourraient être (éventuellement) possible

- Stock total par compagnie
- Produits faibles en stock dans toutes les compagnies
- Mouvements récents toutes compagnies
- Valeur totale du stock
- Comparaison des ventes/sorties
- Transferts en transit inter-company

<mark>TODO</mark>: À réfléchir / définir plus tard.

| Code (`codename`)                   | Description (`name` / `help_text`)                                         | Contexte        | Sensibilité |
|:----------------------------------- |:-------------------------------------------------------------------------- |:---------------:|:-----------:|
| ~~`reporting.[add/change/delete]`~~ | Rapports en lecture seule                                                  | -               | -           |
| reporting.view                      | Lecture des rapports rassemblant les données de plusieurs entreprises      | MULTI_COMPANIES | HIGH        |
| `reporting.stock_levels.view`       | Lecture des rapports de rotations, ruptures imminentes et seuils d'alerte. | MULTI_COMPANIES | HIGH        |
|                                     |                                                                            |                 |             |

 ---

## Rôles par Défaut <a id="roles"></a>

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

## Architecture et séparation des responsabilités <a id="architecture"></a>

### A. Quatre (4) responsabilités, quatre (4) couches

L'architecture est séparée en 4 couches distinctes : 

- **Contexte**: application `scope`, middleware et contexte

- **Cloisonnement**: managers/querysets de l'application `scope`

- **Autorisation**: RBAC et backend, dans l'application `access`

- **Règles métier** : services métier de chaque application

### B. Trois (3) modes conceptuels

Un *mode conceptuel* représente la nature de la requête HTTP en termes de périmètre de données :

- Est-ce que la requête concerne une compagnie spécifique ?
- Est-ce qu'elle concerne plusieurs compagnies ?
- Ou est-ce qu'elle n'a aucun contexte de compagnie ?

`scope` définit 3 modes conceptuels : `UNSCOPED`, `COMPANY` et `MULTI_COMPANIES`.

| Concept         | UNSCOPED                                                                                                                  | COMPANY                                                                                                                                             | MULTI_COMPANIES                                                                                                                                                                                                                                                                                                    |
| --------------- | ------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Description     | Tous les cas légitimes où aucun contexte de compagnie n'existe                                                            | Toutes les demandes concernant une compagnie unique, active. L'`id` de cette compagnie est stockée dans le `ContextVar `par le `CompanyMiddleware`. | Toutes les demandes concernant plusieurs compagnies. La liste des compagnies demandées n'est pas stockée dans le ContextVar.                                                                                                                                                                                       |
| Notes suppl.    |                                                                                                                           | Le statut `is_owner=True`n'élargit jamais les données dans ce type de vue.                                                                          | - Calculée par `CompanyAccessService. authorized_company_ids(user)`  <br/>- Validée strictement : toutes les compagnies demandées doivent être autorisées. Une erreur `PermissionDenied `est levée si ce n'est pas le cas.<br/>- Transmise explicitement au manager : `Product.companies.for_companies([1, 2, 3])` |
| Exemples d'urls | /login, /password-reset<br/>- /g/create-company (OWNER-ONLY),<br/> /g/manage-users<br/>/admin<br/>maintenance, migrations | /c/<company_slug>/products<br/>/c/<company_slug>/move-stock                                                                                         | /mc/dashboard                                                                                                                                                                                                                                                                                                      |

### C. Classification des modèles (globaux vs company-scoped)

Les modèles *company-scoped* héritent de la classe abstraite `CompanyOwned`, qui ajoute le champ `company `(clé étrangère vers le modèle `company.Company`) et des comportements précis: 

- Interdiction de modifier le champ Company après la création

- Définition des managers

| Application | Modèle                                              | Type                                                       |
| ----------- | --------------------------------------------------- | ---------------------------------------------------------- |
| core        | AbstractAudit                                       | Abstract                                                   |
| core        | Image                                               | Selon son modèle référant (pas de champ company explicite) |
| scope       | CompanyOwned                                        | Abstract                                                   |
| access      | Permission<br/>Role<br/>RolePermission<br/>Log      | Global                                                     |
| users       | User<br/>UserHierarchy<br/>UserRole<br/>UserRoleLog | Global                                                     |
| company     | Company                                             | Global                                                     |
| company     | Uom<br/>Location<br/>LocationType                   | Company-Owned                                              |
| catalogue   | Tous les modèles                                    | Company-Owned                                              |
| inventory   | Tous les modèles                                    | Company-Owned                                              |

### D. Trois (3) managers et leur usage selon le mode

Trois managers personnalisés et le contexte (`RequestScope`) sont définis pour chaque modèle *company-owned*.

- **`objects`** : mono-compagnie, contexte initialisé par le `CompanyMiddleware`

- **`companies`** : multi-compagnies, usage explicite

- **`unscoped`**  : non filtré, usage global

Il faut distinguer le `unscoped `object manager d'un modèle `CompanyOwned` de l'utilisation légitime de `object` d'un modèle qui n'est pas lié à une compagnie.

#### CompanyScopedManager

Manager pour les requêtes mono-compagnie. Utilise `ContextVar `pour stocker la compagnie demandée par l'URL grâce au `CompanyMiddleware`.

Le rôle du `CompanyScopedManager` est de filtrer les données selon l'entreprise active (ou contexte courant).

Ainsi,

```python
Product.objects.all()
```

dans l'url `/c/company-a/products/` retournera seulement les produits de l'entreprise dont le slug est *company-a*. À noter qu'une vue *company-scoped* reste *company-scoped* même pour le propriétaire (qui a le droit de tout voir mais à partir d'autres vues).

#### CompaniesScopedManager

Manager pour les requêtes multi-compagnies. Nécessite un appel explicite à `for_companies(company_ids). `**Validation** : Lève l'exception `MissingCompaniesScope `si `for_companies()` n'est pas appelé.

**Usage** :

```python
Product.companies.for_companies([1, 2, 3])
```

#### UnscopedManager

Manager par défaut pour les modèles company-scoped en mode UNSCOPED. Retourne un queryset non filtré.

**Usage légitime** :

- Vues globales sans contexte de compagnie (/g/*, /login)
- Admin Django avec `get_queryset()` explicite
- Migrations et commandes de maintenance

**Attention** : Ce manager ne doit jamais être utilisé dans une vue company-scoped (/c/<slug>/...).

#### Interaction entre modes conceptuels et managers

| Mode conceptuel | URLs typiques             | Manager pour modèles  globaux       | Managers pour modèles company-scoped                            |
| --------------- | ------------------------- | ----------------------------------- | --------------------------------------------------------------- |
| UNSCOPED        | /login, /g/create-company | objects (manager django par défaut) | `unscoped` (`UnscopedManager`)                                  |
| COMPANY         | /c/<slug>/products        | N.A.                                | `objects` - automatique, avec contexte (`CompanyScopedManager`) |
| MULTI_COMPANIES | /mc/dashboard             | N.A.                                | `companies.for_companies(ids)` (`CompaniesScopedManager`)       |

### E. Tableau récapitulatif

| Scénario type        | URL pattern             | Mode conceptuel | Type de modèle           | Manager utilisé                                         | Contexte de validation                        |
| -------------------- | ----------------------- | --------------- | ------------------------ | ------------------------------------------------------- | --------------------------------------------- |
| Authentification     | /login, /password-reset | UNSCOPED        | Global (User)            | `objects` (Django)                                      | Aucun                                         |
| Création compagnie   | /g/create-company       | UNSCOPED        | Global (Company)         | `objects` (Django)                                      | OWNER-ONLY                                    |
| Gestion utilisateurs | /g/manage-users         | UNSCOPED        | Global (User)            | `objects` (Django)                                      | SYSTEM permissions                            |
| Admin Django         | /admin                  | UNSCOPED        | Mixte                    | `objects` (Django)                                      | `get_queryset()` explicite                    |
| Vue company-scoped   | /c/<slug>/products      | COMPANY         | Company-scoped (Product) | `objects` (CompanyScopedManager)                        | ContextVar + RBAC COMPANY                     |
| Vue multi-compagnies | /mc/dashboard           | MULTI_COMPANIES | Company-scoped (Product) | `companies.for_companies(ids)` (CompaniesScopedManager) | `CompanyAccessService` + RBAC MULTI_COMPANIES |

 ---

## CompanyMiddleware <a id="middleware"></a>

`CompanyMiddleware` sert à établir le **contexte d'entreprise courante** pour les URLs company-scoped

**Responsabilités** :

1. détecter les URLs contenant un slug d'entreprise (/c/<company-slug>/...)  ;
2. résoudre le company-slug (lever une erreur 404 si inexistant alors qu'on est dans un pattern /c/) ;
3. attacher la compagnie à la requête `request` ;
4. installer le contexte `ContextVar` pour le `CompanyScopedManager`;
5. nettoyer ce contexte après la requête dans un `finally`.

**Responsabilités exclues** :

- Le middleware ne vérifie PAS l'accès à la compagnie (403)
- Le middleware ne vérifie PAS les permissions métier granulaires
- Ces validations sont effectuées par le backend RBAC et les services métier

**Implémentation** :

- Utilisation de regex dans la partie ascendante, pour envoyer un 404 avant le traitement django
  - process_view() permettrait d'utiliser l'infrastructure de django et éviterait de dupliquer la logique de routage: à envisager pour optimisation future, surtout si patterns complexes.
- Stocke l'objet [Company](cci:2://file://wsl.localhost/Ubuntu/home/caroline/django-stock/src/company/models/company.py:4:0-27:33) complet dans `request.company`, pour la vue (contrairement à `ContextVar`, qui contient seulement `company_id` et `is_active`, pour les managers)
- Utilise `RequestScope` avec le mode `COMPANY`

```python
request.company = company_obj  # Objet complet
RequestScope.set_company_scope(company_id, is_active)  # ContextVar minimal
```

- Distinction claire 404 (slug inexistant) vs 403 (compagnie interdite)

**Exemple d'utilisation** :

```python
# Dans une vue company-scoped
def product_list(request):
 company = request.company # Défini par le middleware
 products = Product.objects.all() # Auto-filtré par CompanyScopedManager
 return render(request, 'products.html', {'products': products})
```

`CompanyMiddleware` par le `PermissionService`.

---

## Intégrité inter-compagnie - prévention des relations incohérente sur le champs compagnie <a id="integrity"></a>

Chaque modèle company-scoped hérite du modèle abstrait CompanyOwned, défini dans l'application scope. Ce modèle défini la clé étrangère company et bloque la mise à jour du champ company après la création. 

Pour chaque modèle, il y a aussi l'invariant suivant :

```python
objet.company_id = relation.company_id
```

Ainsi, pour nommer quelques exemples :

- Si Stock.company_id = id de companie-a, tous les produits référencés doivent aussi être des produits de A ;

- Si Location.company_id = A, tous les enfants de cette location doivent aussi avoir company_id = A ;

- Si AttributeKey.company_id = A, tous ses AttributeValue.company_id doivent aussi être A. 

Pour prévenir ces incohérences, plusieurs garde-fous sont prévus:

- **Contrainte d'intégrité inter-tables** : la garantie ultime qui empêche toute incohérence ;

- **Validation métier avant save** (service / clear() ) : messages clairs et UX propre ;

- **Querysets filtrés** (forms/serializers/admin) : ne proposer que des objets de la même compagnie ;

- **Tests dédiés** : un set "validation applicative" et un set "contrainte DB".

### Contrainte d'intégrité inter-tables

Django ne supporte pas nativement les contraintes d'intégrité inter-tables mais les SGDB les supportent (dont MySQL). Il est possible de les ajouter manuellement directement dans les fichiers migrations.

Exemple: 

- Sur `LocationType`: `UNIQUE(id, company_id)`

- Sur `Location`: `FOREIGN KEY (parent_id, company_id) REFERENCES company_locationtype(id, company_id)`

| Modèle                               | Contraintes inter-tables                                                                                                                                                                                                                                                                        |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `company.`<br/> `Location`           | `FOREIGN KEY (location_type_id, company_id) REFERENCES company_locationtype(id, company_id)`<br/><br/>`FOREIGN KEY (parent_id, company_id) REFERENCES company_location(id, company_id)` - attention `parent_id` est `NULLABLE` pour laisser passer les racines                                  |
| `company.`<br/> `Address`            | `FOREIGN KEY (location_id, company_id) REFERENCES company_location(id, company_id)`                                                                                                                                                                                                             |
| `catalogue.`<br/> `Category`         | `FOREIGN KEY (parent_id, company_id) REFERENCES catalogue_category(id, company_id)` - attention `parent_id` est `NULLABLE` pour laisser passer les catégories racines                                                                                                                           |
| `catalogue.`<br/> `ProductModel`     | `FOREIGN KEY (category_id, company_id) REFERENCES catalogue_category(id, company_id)`                                                                                                                                                                                                           |
| `catalogue.`<br/> `Product`          | `FOREIGN KEY (productmodel_id, company_id) REFERENCES catalogue_productmodel(id, company_id)`                                                                                                                                                                                                   |
| `catalogue.`<br/> `ProductImage`     | `FOREIGN KEY (product_id, company_id) REFERENCES catalogue_product(id, company_id)`                                                                                                                                                                                                             |
| `catalogue.`<br/> `ProductPackaging` | `FOREIGN KEY (product_id, company_id) REFERENCES catalogue_product(id, company_id)`<br/><br/>`FOREIGN KEY (base_uom_id, company_id) REFERENCES company_uom(id, company_id)`                                                                                                                     |
| `catalogue.`<br/> `Attribute`        | `FOREIGN KEY (productmodel_id, company_id) REFERENCES catalogue_productmodel(id, company_id)`                                                                                                                                                                                                   |
| `catalogue.`<br/> `AttributeValue`   | `FOREIGN KEY (attribute_id, company_id) REFERENCES catalogue_attribute(id, company_id)`                                                                                                                                                                                                         |
| `catalogue.`<br/> `ProductVariant`   | `FOREIGN KEY (product_id, company_id) REFERENCES catalogue_product(id, company_id)`                                                                                                                                                                                                             |
| `catalogue.`<br/> `VariantOption`    | `FOREIGN KEY (variant_id, company_id) REFERENCES catalogue_productvariant(id, company_id)`<br/><br/>`FOREIGN KEY (attributevalue_id, company_id) REFERENCES catalogue_attributevalue(id, company_id)`                                                                                           |
| `catalogue.`<br/> `ProductTag`       | `FOREIGN KEY (product_id, company_id) REFERENCES catalogue_product(id, company_id)`<br/><br/>`FOREIGN KEY (tag_id, company_id) REFERENCES catalogue_tag(id, company_id)`                                                                                                                        |
| `inventory`. <br/>`Stock`            | `FOREIGN KEY (product_id, company_id) REFERENCES catalogue_product(id, company_id)`<br/><br/>`FOREIGN KEY (location_id, company_id) REFERENCES company_location(id, company_id)`<br/><br/>`FOREIGN KEY (productpackaging_id, company_id) REFERENCES catalogue_productpackaging(id, company_id)` |

---

## Sécurisation des interfaces et des points d'accès <a id="endpoints"></a>

### Prévention des failles IDOR (Insecure Direct Object Reference) <a id="idor"></a>

Pour empêcher qu'un utilisateur n'accède aux données d'une autre entreprise en devinant ou en incrémentant les identifiants numériques dans les URLs (ex: `/products/42/`), le projet adopte une stratégie de double identification :

* **company_id + slug** : Un index unique composite composé de l'id d'entreprise et d'un slug. Utilisé pour les entités visibles (company, location, category, product). L'url utilisera alors le slug (ex: `/c/company-slug/product/product-slug`).
* **Clés publiques d'exposition (UUIDv4)** : Un champ `uuid` (`UUIDField`) aléatoire et unique pour les tables aux données sensibles ou moins exposées (ex: `/g/uuid`, `/c/company-slug/uuid`).

À noter que les table utilisent une **Clés primaires internes**, c'est à dire un `BigAutoField` auto-incrémenté classique, pour optimiser les performances des index et des jointures au niveau du SGDB.

### Protection contre les attaques par force brute (Authentication Rate Limiting)

Pour empêcher la découverte de mots de passe par force brute ou par dictionnaire (credential stuffing), l'application implémente un mécanisme de verrouillage dynamique :

* **Utilisation de `django-axes`** : Le projet intègre la librairie standard `django-axes` au niveau de la couche des middlewares.
* **Verrouillage hybride (IP + Username)** : Les tentatives infructueuses sont suivies à la fois par l'adresse IP source et par l'identifiant (email) soumis. Cela permet de bloquer un attaquant ciblé sans verrouiller l'accès de l'utilisateur légitime si celui-ci se connecte depuis un autre réseau.
* **Seuil de tolérance et refroidissement** : Après 5 tentatives de connexion échouées dans une fenêtre de 5 minutes, l'adresse IP concernée est temporairement bannie (HTTP 423) pour une durée configurable. Chaque événement de blocage est enregistré de manière immuable pour permettre une analyse de sécurité ultérieure.

---

## Isolation hermétique du contexte d'entreprise (Thread-Safety) <a id="thread-safety"></a>

Le projet utilise un modèle de base de données partagée où le filtrage repose sur le code applicatif (`CompanyScopedManager`). Pour éviter les risques de fuite de données en mémoire entre deux requêtes simultanées de clients différents (Thread Context Bleeding), le stockage de la compagnie active respecte les règles suivantes :

1. **Bannissement des variables globales** : Aucune variable globale ou attribut de classe statique n'est utilisé pour stocker l'entreprise ou l'utilisateur connecté.
2. **Utilisation de `Contextvars`** : Le `CompanyMiddleware` utilise le module natif `contextvars` de Python (via un conteneur thread-safe) pour isoler la compagnie active au sein du cycle de vie unique de la requête HTTP en cours.
3. **Cycle de vie strict (Nettoyage)** : À la fin de chaque cycle de requête/réponse (dans le bloc `finally` du middleware), le contexte est explicitement réinitialisé. Cela garantit qu'un thread de serveur web (comme Gunicorn ou uWSGI) réutilisé pour un autre client redémarre avec une mémoire vierge de toute information d'entreprise précédente.

```python
import contextvars

# Ce conteneur est isolé par thread et par tâche asynchrone
_current_company = contextvars.ContextVar("current_company", default=None)

class CompanyContext:
    @staticmethod
    def set(company):
        _current_company.set(company)

    @staticmethod
    def get():
        return _current_company.get()

    @staticmethod
    def clear():
        _current_company.set(None)
```

Le code dans CompanyMiddleware: appel de `CompanyContext.set(company)` au début et `CompanyContext.clear()` dans un bloc `finally`.

---

## Plan de tests <a id="tests"></a>

Les tests de sécurité doivent couvrir au minimum :

- un propriétaire peut accéder à toutes les compagnies ;
- un propriétaire ne voit que la compagnie courante dans une vue `/c/<company_slug>/...` ;
- un employé ne peut accéder qu'aux compagnies autorisées ;
- un employé ne peut pas accéder aux vues multi-companies`/mc/...` sans la permission MULTI_COMPANIES exigée par cette fonctionnalité;
- un employé autorisé peut créer un autre employé ;
- un employé ne peut pas créer, modifier ou désactiver un propriétaire ;
- il est impossible de désactiver le dernier propriétaire actif ;
- il est impossible d'obtenir un état sans propriétaire actif ;
- les modèles company-scoped ne retournent jamais des données hors scope courant ;

### Tests owner

- owner peut accéder à /c/company-a/...;
- owner peut accéder à /c/company-b/...;
- owner peut accéder à /mc/dashboard/;
- owner voit les rapports consolidés ;
- owner peut gérer les rôles ;
- owner peut créer une compagnie ;
- owner peut voir les mouvements de toutes les compagnies dans une vue multi-companies.

### Tests employés

- employé de A peut accéder à A ;
- employé de A ne peut pas accéder à B ;
- employé de A ne peut pas accéder à `/mc/...` sans la permission appropriée;
- employé de A et B peut accéder à A (/c/company-a/...) et B (/c/company-b/) ;
- employé avec location limitée ne voit pas les autres locations ;
- employé sans permission stock ne peut pas modifier stock.

### Tests employés avec MULTI_COMPANIES (/mc/...)

- employé sans permission MULTI_COMPANIES → 403 ;
- employé avec la permission et accès à A et B → voit A et B ;
- employé avec la permission et accès seulement à A → voit seulement A par défaut ;
- employé autorisé à A demandant explicitement [A, B] → 403, aucun résultat partiel ;
- rôle ou assignation inactif → accès refusé ou compagnie exclue ;
- permission reporting.view ne donne aucun droit de modification ;
- owner → toutes les compagnies actives pertinentes ;
- compagnie archivée → exclue selon la règle actuelle.

### Tests context

- sur /c/company-a/..., même owner voit par défaut les données de A seulement ;

- sans contexte explicite, les requêtes échouent.

## Extension des Tests de Sécurité (Couverture Matrice RBAC)

#### Tests de validation de la Matrice RBAC

##### 1. Cas d'usage : Permissions de type "Compagnie & Lieu" (`context = True`)

Ces tests vérifient le comportement des droits métier spécifiques à une entité (ex: `catalogue.product.delete`).

###### Cas 1.1 : Permission Globale / Rôle Global / Assignation Globale

- **Données DB :** `role.company_id = NULL`, `userrole.company_id = NULL`, `userrole.location_id = NULL`
- **Test :** L'employé peut exécuter l'action sur la Compagnie A (Lieu X) **ET** sur la Compagnie B (Lieu Y).
- **Résultat attendu :** Succès partout.

###### Cas 1.2 : Permission Globale / Rôle Global / Assignation Restreinte (Compagnie seule)

- **Données DB :** `role.company_id = NULL`, `userrole.company_id = company-a`, `userrole.location_id = NULL`
- **Test A :** L'employé tente l'action sur la Compagnie A. *(Attendu : Succès)*
- **Test B :** L'employé tente l'action sur la Compagnie B. *(Attendu : Échec / 403 Forbidden)*

###### Cas 1.3 : Permission Globale / Rôle Global / Assignation Restreinte (Compagnie + Lieu)

- **Données DB :** `role.company_id = NULL`, `userrole.company_id = id de company-a`, `userrole.location_id = Entrepot_Paris`
- **Test A (Même Lieu) :** Action demandée sur la Compagnie A au lieu `Entrepot_Paris`. *(Attendu : Succès)*
- **Test B (Lieu Enfant) :** Action demandée sur la Compagnie A au lieu `Allee_01_Paris` (enfant direct de `Entrepot_Paris`). *(Attendu : Succès)*
- **Test C (Lieu Parent ou Cousin) :** Action demandée sur la Compagnie A au lieu `Siege_Lyon` ou au niveau racine de la compagnie. *(Attendu : Échec / 403)*
- **Test D (Autre Compagnie) :** Action demandée sur la Compagnie B au lieu `Entrepot_Paris`. *(Attendu : Échec / 403)*

###### Cas 1.4 : Permission Spécifique (Rôle lié à une Compagnie) / Assignation Globale

- **Données DB :** `role.company_id = id de company-a`, `userrole.company_id = NULL`, `userrole.location_id = NULL`
- **Test A :** L'employé tente l'action sur la Compagnie A. *(Attendu : Succès - l'entonnoir valide la Compagnie A)*
- **Test B :** L'employé tente l'action sur la Compagnie B. *(Attendu : Échec / 403 - car la permission elle-même est exclusive à A)*

###### Cas 1.5 : Permission Spécifique (Rôle lié à une Compagnie) / Assignation Restreinte (Même Compagnie)

- **Données DB :** `role.company_id = id de company-a`, `userrole.company_id = id de company-a`, `userrole.location_id = NULL`
- **Test :** L'employé tente l'action sur la Compagnie A.
- **Résultat attendu :** Succès.

###### Cas 1.6 : Permission Spécifique / Assignation Restreinte (Même Compagnie + Lieu)

- **Données DB :** `role.company_id = id de company-a`, `userrole.company_id = id de company-a`, `userrole.location_id = Entrepot_Paris`
- **Test A (Lieu Exact) :** Action demandée sur la Compagnie A à `Entrepot_Paris`. *(Attendu : Succès)*
- **Test B (Lieu Enfant) :** Action demandée sur la Compagnie A à `Allee_01_Paris`. *(Attendu : Succès)*
- **Test C (Lieu Hors Scope) :** Action demandée sur la Compagnie A à `Entrepot_Marseille`. *(Attendu : Échec / 403)*

###### Cas 1.7 : Permission Spécifique / Assignation Restreinte (Compagnie différente) -> Conflit

- **Données DB :** `role.company_id = id de company-a`, `userrole.company_id = id de company-b,`userrole.location_id = NULL`
- **Test :** L'employé tente l'action sur la Compagnie A (ou la Compagnie B).
- **Résultat attendu :** Échec / 403 partout *(Conflit de configuration en base de données)*.

---

##### 2. Cas d'usage : Permissions de type "Global" (`need_globalcontext = True`)

Ces tests ciblent les actions d'administration système ne dépendant pas d'une entité commerciale (ex: `core.settings.change`).

###### Cas 2.1 : Permission Globale / Assignation Totalement Globale

- **Données DB :** `role.company_id = NULL`, `userrole.company_id = NULL`, `userrole.location_id = NULL`
- **Test :** L'utilisateur tente d'accéder à la configuration système globale sur une route `/g/...` sans spécifier de compagnie.
- **Résultat attendu :** Succès.

###### Cas 2.2 : Permission Globale / Assignation Restreinte à une Compagnie

- **Données DB :** `role.company_id = NULL`, `userrole.company_id = id de company-a`, `userrole.location_id = NULL`
- **Test :** L'utilisateur tente d'accéder à l'action globale.
- **Résultat attendu :** Échec / 403 *(Un droit global ne peut être exercé par un utilisateur dont le rôle est cloisonné à une filiale)*.

###### Cas 2.3 : Permission Globale / Assignation Restreinte à un Lieu

- **Données DB :** `role.company_id = NULL`, `userrole.company_id = NULL`, `userrole.location_id = Entrepot_Paris`
- **Test :** L'utilisateur tente d'accéder à l'action globale.
- **Résultat attendu :** Échec / 403 *(Même logique, restriction trop sévère pour du global)*.

---

##### Tests des Limites et Robustesse (Edge Cases)

Validation des paramètres de la fonction de service

- **Test Absence de Contexte Compagnie :** Appeler la méthode `has_perm()` pour une permission de type `context=COMPANY` en passant `context=None`. *(Attendu : Retourne `False` immédiatement).*
- **Test Lieu Inexistant / Supprimé :** L'utilisateur possède un `userrole.location_id = 9999` qui a été supprimé de la base de données entre-temps. L'appel doit intercepter l'erreur `DoesNotExist` proprement. *(Attendu : Retourne `False` sans faire crasher l'application).*
- **Test Boucle Multi-Rôles (Cumul des droits) :** L'utilisateur possède deux rôles distincts :
  - Le Rôle 1 l'autorise sur la Compagnie A (Lieu exact `Paris`).
  - Le Rôle 2 l'autorise sur la Compagnie A (Lieu exact `Lyon`).
  - **Test :** L'utilisateur demande l'accès pour la Compagnie A à `Lyon`. Le système doit analyser le Rôle 1 (qui échoue), continuer la boucle, analyser le Rôle 2 et enfin accorder l'accès. *(Attendu : Retourne `True`)*.

### Test natif de Django pour `user.has_perm`

L'intégration native dans `user.has_perm` simplifie l'écriture des tests car il est possible d'utiliser le test natif de Django (`django.test.Client`) ou simuler les requêtes en alimentant manuellement le conteneur `CompanyContext` lors du `setUp` des tests.

Pour tester le cloisonnement, la configuration actuelle est idéale :

1. Les tests simuleront des requêtes sur les URLs .
2. Le `CompanyMiddleware` s'exécutera.
3. Le `CompanyContext` sera alimenté.
4. `user.has_perm()` interceptera la bonne compagnie sans aucune plomberie additionnelle.

---
