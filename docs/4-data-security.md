<div align="center">

<img src="../assets/img/logo.svg" alt="Logo Gestion de stocks" width="60" />

# Sécurité des données et contrôle d'accès

Projet Gestion de stocks — document de conception

![Statut](https://img.shields.io/badge/Statut_du_document-En_cours_de_rédaction-purple.svg)

<h3>

[Sécurisation endpoints](#endpoints) | [Custom RBAC](#rbac) | [CompanyMiddleware](#midleware) | [CompanyScopedManager](#manager) | [Thread-Safety](#thread-safety)  | [Permissions](#permissions) | [Roles](#roles) | [Tests de sécurité](#tests)

</h3>

</div>

Ce document discute de la sécurité des données et du contrôle d'accès et présente la structure du système de contrôle d'accès basé sur les rôles (**RBAC - Role-Based Access Control**) personnalisé et les barrières de sécurité qui seront mises en place.

[← Analyse](3-choices-and-analysis.md) | [Sommaire](2-conception.md) |  [Modules →](5-django-apps-and-urls.md)

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

## RBAC personnalisé <a id="rbac"></a>

Les permissions métier sont gérées par un système custom. Les modèles sont définis dans l'application `access` alors que le modèle permettant d'assigner un rôle à un utilisateur appartient à l'application `users`.

### Descriptions des modèles du contrôle d'accès

<img src="schema_database_access.svg" alt="Schema access tables" width=400 />
<img src="schema_database_userrole.svg" alt="Schema userrole table" width=400 />

| table                    | Description                                                                                                                                                                                                                                                                                                           |
|:------------------------ |:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `access_permission`      | Stocke les permissions fonctionnelles de l'application (ex:`codename = "inventory.movement.sale"`). Contrairement au CRUD global de Django, ces permissions décrivent des actions métiers précises.                                                                                                                   |
| `access_role`            | Regroupe un ensemble de permissions sous un identifiant unique<br/><br/>** Clé stratégique** : Le champ `company_id FK (NULLABLE)`. S'il est `NULL`, le rôle est **global** (ex: le rôle *Gestionnaire* existe pour toutes les entreprises). S'il est renseigné, le rôle est spécifique à une seule entreprise.       |
| `access_rolepermissions` | **Liste des permissions d'un rôle**<br/> Table d'association entre les permissions et les rôles. Permet de définir les permissions associées à chaque rôle.                                                                                                                                                           |
| `access_log`             | **Audit** <br/>Enregistre de manière immuable chaque action de modification sur le système d'accès (création de rôle, changement de permissions). Elle utilise un champ `JSONField` (`snap_infos`) pour stocker les infos au moment de la transaction et des FK pour permettre la recherche / filtre plus facilement. |
| `users_userrole`         | **Table d'assignation**<br/> Cœur du système. Elle associe un utilisateur à un rôle, et y ajoute aussi un **scope (périmètre de validité)**.                                                                                                                                                                          |
| users_userrolelog        | **Audit**<br/>Enregistre de manière immuable chaque action de modification sur les attributions de rôles aux utilisateurs. Elle utilise un champ `JSONField` (`snap_infos`) pour stocker les infos au moment de la transaction et des FK pour permettre la recherche / filtre plus facilement.                        |

#### Matrice de décision RBAC concernant les permissions

##### Partie 1 : Permissions de type "Compagnie & Lieu" (`need_companycontext = True`)<a id="matriceRBAC"></a>

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

Le système de permissions natif de Django est conçu pour être étendu et remplacé grâce à un mécanisme appelé **Authentications Backends***. Ainsi, la question des permissions du Custom RBAC peut être répondu avec `user.has_perm()` avec, en coulisse, un arbre de décision custom. 

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
                      [ Trouver la Permission demandée ]
                                     │
                                     ├── Introuvable OU `is_active == False` ──> RETOURNER FAUX
                                     ▼
                        [ Boucle sur chaque UserRole ]
                                     │
                         `is_active == False` OU rôle associé inactif ──> Passer au suivant
                                     │
                                     ▼
                  Quels sont les besoins de la Permission ?
                    ├── Global  ──> L'assignation doit être 100% vide (Compagnie = NULL, Lieu = NULL)
                    └── Company ──> La Compagnie matche-t-elle le contexte ?
                                       │
                                       └── [Oui] ──> La location matche-t-elle (ou est-elle un enfant) ?
                                       │                │
                                       │                └── [Oui] ──> RETOURNER VRAI                 
                                       │
                                       └── [Non] ──> RETOURNER FAUX
```

#### Backend d'Authentification personnalisé <a id="auth-backend"></a>

```python
# django-stock/src/access/backends.py

from django.db.models import Prefetch
from django.core.exceptions import ObjectDoesNotExist
# Importez les modèles ici (UserRole, AccessPermission, CompanyLocation, etc.)

class CompanyRBACBackend:
    """
    Backend de permission personnalisé pour gérer le RBAC par Compagnie et Lieu.
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
        :param obj: Un dictionnaire optionnel contenant le contexte : 
                    {"company_id": X, "location_id": Y}
        """
        # 1. Protection & Fast-Bypass
        if not user_obj or not user_obj.is_active:
            return False

        if getattr(user_obj, 'is_owner', False):
            return True

        # 2. Détermination automatique du contexte de compagnie
        context_company_id = None
        context_location_id = None

        if isinstance(obj, dict):
            context_company_id = obj.get('company_id')
            context_location_id = obj.get('location_id')
        else:
            # Récupération automatique depuis le CompanyContext (Thread-Safe)
            current_company = CompanyContext.get()
            if current_company:
                context_company_id = current_company.id

            # Si obj est directement une instance de modèle "Location", on extrait son ID
            if hasattr(obj, 'location_id'): # Si c'est un objet possédant un lieu (ex: Stock)
                context_location_id = obj.location_id
            elif hasattr(obj, 'path'): # Si obj est directement l'instance de CompanyLocation
                context_location_id = obj.id

        # 3. Récupération TOUT-EN-UN (Filtres is_active inclus)
        user_roles = UserRole.objects.filter(
            user_id=user_obj.id,
            is_active=True,         # Validation de l'assignation active
            role__is_active=True    # Validation du rôle actif
        ).select_related(
            'role', 
            'location'
        ).prefetch_related(
            Prefetch(
                'role__permissions',
                queryset=AccessPermission.objects.filter(codename=perm, is_active=True), # Permission active
                to_attr='matching_permissions'
            )
        )

        if not user_roles:
            return False

        context_location_path = None

        # 4. Évaluation en mémoire Python
        for user_role in user_roles:
            role = user_role.role

            if not role.matching_permissions:
                continue

            permission = role.matching_permissions[0] # Récupère la perm de la liste to_attr

            # --- CAS CONTEXTE GLOBAL ---
            if permission.need_globalcontext and not permission.need_companycontext:
                if user_role.company_id is None and user_role.location_id is None:
                    return True
                continue

            # --- CAS CONTEXTE COMPAGNIE ---
            elif permission.need_companycontext:
                if context_company_id is None:
                    continue

                company_access_granted = False

                if role.company_id is None and user_role.company_id is None:
                    company_access_granted = True

                elif role.company_id is not None:
                    if role.company_id == context_company_id:
                        if user_role.company_id is None or user_role.company_id == context_company_id:
                            company_access_granted = True

                elif role.company_id is None and user_role.company_id is not None:
                    if user_role.company_id == context_company_id:
                        company_access_granted = True

                if not company_access_granted:
                    continue

                # --- ÉTAPE B : VALIDATION DU PÉRIMÈTRE LOCATION ---
                if user_role.location_id is None:
                    return True 

                if context_location_id is not None:
                    if user_role.location_id == context_location_id:
                        return True

                    if user_role.location and user_role.location.path:
                        if context_location_path is None:
                            try:
                                context_location_path = CompanyLocation.objects.values_list('path', flat=True).get(id=context_location_id)
                            except CompanyLocation.DoesNotExist:
                                context_location_path = ""

                        parent_path = user_role.location.path
                        if context_location_path.startswith(parent_path) and len(context_location_path) > len(parent_path):
                            return True

        return False
```

<mark>TODO</mark>: Modifs à prévoir à l'arbre de décision et à la méthode has_perm ci-haut:

1. Pour les mouvements d'inventaire, on a ajouté les permissions génériques `inventory.stock.decrease` et `inventory.stock.increase`
* Donc avec cette version de has_perm, il faut faire 2 demandes. Par exemple:  if `user.has_perm("inventory.stock.increase")` or `user.has_perm("inventory.stock.purchase")`

* Or, les mouvements d'inventaire sont la base de tout le système et sont donc très fréquents. Il serait vraiment mieux de pouvoir faire 1 seul has_perm en vérifiant les deux permissions OR en même temps.

* Donc arbre de décision: 
  
  * [ Trouver la Permission demandée ] devient [ Trouver la ou les Permission(s) demandée(s) ]

* Et has_perm peut être appelée ainsi (*1 seule requête en DB*).
  
  * if `user.has_perm("inventory.stock.increase OR inventory.stock.purchase"])`. Donc has_perm doit commencé par nettoyer le paramètre perm s'il contient des espaces et le mot clé OR (en majuscule).
  
  * Une ValidationError est lancée si le paramètre est mal paramétré (contient autre chose que "OR")
2. Les concepts de` access_permission.need_globalcontext ` et `access_permission.need_companycontext ` ont été regroupé sous `context`, un enum pouvant prendre les valeurs de : `SYSTEM`, `COMPANY`, `MULTI_COMPANIES`, `LOCATION `et `MULTI_LOCATIONS`
* Implications: une permission GLOBALE est devenue, plus explicitement, une permission `SYSTEM `(pas besoin de company active) ou `MULTI_COMPANIES `(besoin de permissions sur plusieurs compagnies - c'est probablement une vue de rapport d'aggrégation de données.). Il y a aussi l'ajout du niveau de scope `LOCATION `et `MULTI_LOCATIONS`.
  
  * `LOCATION `et `MULTI_LOCATIONS `sont des scopes `COMPANY`spécialisés

* Ainsi: on doit maintenant pouvoir appeler user.has_perm avec le param obj (dictionnaire de contexte) où obj est: 
  
  * {"company_id": X} => Pour vérifier une perm de context COMPANY
  
  * {"company_id": X, "location_id": A} => Pour vérifier une perm de context LOCATION
  
  * {"company_id": X, "location_id": [A, B]} => Pour vérifier une perm de context MULTI_LOCATIONS
  
  * {"company_id": [X, Y]} => Pour vérifier une perm de context MULTI_COMPANIES
  
  * {"company_id": [X, Y], "location_id": ...} => INVALIDE. une perm de context MULTI-COMPANIES ne descend pas jusqu'à préciser des locations.

##### Enregistrer le Backend dans `settings.py`

```python
# django-stock/src/config/settings.py

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend', # Le backend par défaut de Django
    'mon_projet.authentication.backends.CompanyRBACBackend', # Votre nouveau backend
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
    print("L'utilisateur a le droit de supprimer ce produit dans cette filiale.")
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

## CompanyMiddleware <a id="middleware"></a>

`CompanyMiddleware `sert à établir le **contexte d'entreprise courante** pour les URLs company-scoped

**Responsabilités**:

1. détecter les URLs contenant un slug d'entreprise (/c/<company_slug>/...) ;
2. charger la compagnie correspondante
3. vérifier que la compagnie est active ;
4. vérifier que l’utilisateur peut accéder à cette compagnie :
   * si user est inactif : refuser l'accès ;
   * si user est owner : autoriser l'accès ;
   * sinon : vérifier le scope RBAC pour cette entreprise ;
5. attacher la compagnie à la requête :

```python
   request.company = company
```

6. définir le contexte utilisé par `CompanyScopedManager `;
7. nettoyer ce contexte après la requête.

`CompanyMiddleware` vérifie l'accès à la compagnie mais il ne remplace pas les permissions métier granulaires. Les actions comme modifier un produit, ajuster un stock ou créer un employé doivent être validées par le `PermissionService`.

---

## CompanyScopedManager <a id="manager"></a>

Le rôle du `CompanyScopedManager` est de filtrer les données selon l'entreprise active (ou contexte courant).

Ainsi,

```python
Product.objects.all()
```

dans l'url `/c/company-a/products/` retournera seulement les produits de l'entreprise dont le slug est *company-a*. À noter qu'une vue *company-scoped* reste *company-scoped* même pour le propriétaire (qui a le droit de tout voir mais à partir d'autres vues).

Les vues globales owner doivent utiliser des accès explicites et protégés, et non contourner implicitement le filtrage dans les vues company-scoped.

---

### Isolation hermétique du contexte d'entreprise (Thread-Safety) <a id="thread-safety"></a>

Le projet utilise un modèle de base de données partagée où le filtrage repose sur le code applicatif (`CompanyScopedManager`). Pour éviter tout risque de fuite de données en mémoire entre deux requêtes simultanées de clients différents (Thread Context Bleeding), le stockage de la compagnie active respecte les règles suivantes :

1. **Bannissement des variables globales** : Aucune variable globale ou attribut de classe statique n'est utilisé pour stocker l'entreprise ou l'utilisateur connecté.
2. **Utilisation de `contextvars`** : Le `CompanyMiddleware` utilise le module natif `contextvars` de Python (via un conteneur thread-safe) pour isoler la compagnie active au sein du cycle de vie unique de la requête HTTP en cours.
3. **Cycle de vie strict (Nettoyage)** : À la fin de chaque cycle de requête/réponse (dans le bloc `finally` du middleware), le contexte est explicitement réinitialisé. Cela garantit qu'un thread de serveur web (comme Gunicorn ou uWSGI) réutilisé pour un autre client redémarre avec une mémoire totalement vierge de toute information d'entreprise précédente.

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

## Référentiel des permissions <a id="permissions"></a>

Les permissions sont créées lors de la configuration initiale de l'application.

Les permissions suivent le modèle suivant: *[app_name].[model_name].[OPT][perm_type]*.

- *perm_type* reprend les CRUD officiels de django (`view`, `add`, `change`, delete`) `et les étend en les regroupant parfois (ex: `manage`) ou en ciblant un champs spécifique et/ou la valeur permise (ex: `activate `dans `users.user.activate`  permet de mettre le field `is_active `de l'utilisateur à vrai)
- *model_name* est parfois sauté car la permission concerne plusieurs tables (ex: `access.manage` permet de faire des changements dans les tables `access_role `et `access_rolepermissions`)
- *OPT* est optionnel et est utilisé pour quelques permissions (ex: `company.location.main.add` et `company.location.sub.add` permettent respectivement de créer des emplacements de haut niveau (location racine, sans aucun parent)  et des emplacements de sous-location (location enfant)

> [!TIP]
> *Les fonctionnalités sous-jacentes à chaque permission seront implémentées à différents stades du développement. Certaines permissions sont projetées mais pourraient être codé différemment selon l'évolution du produit et de l'UX.*

### Légende et explications

#### Contexte

Défini le périmètre de la permission. Les contextes possibles sont`SYSTEM`,`COMPANY`, `MULTI_COMPANIES`, `LOCATION `ou `MULTI_LOCATIONS`. 

##### Scope SYSTEM (`access_permission.context = SYSTEM`)

La permission concerne une configuration externe aux compagnies (*ex: création d'utilisateur, téléversement d'images sur le serveur*) 

##### Scope COMPANY (`access_permission.context = COMPANY`)

La permission s'applique exclusivement dans un contexte d'entreprise active.

*Exemples:  L'utilisateur authentifié a la permission `catalogue.product.add` valide pour l'Entreprise A seulement.*

- `.../c/entreprise-a/product/add` => Accès granted

- `.../c/entreprise-b/product/add` => Error Permission denied

-  `.../c/notexistslugcompany/product/add` => Error Permission denied

- `.../product/add` => Error Company Context Missing

##### Scope  MULTI COMPANIES (`access_permission.context = MULTI_COMPANIES`)

La permission concerne une demande d'aggrégation (rapport consolidé sur plusieurs compagnies).

##### Scope LOCATION (`access_permission.context = LOCATION`)

La permission s'applique exclusivement dans un contexte d'entreprise active ET pour une location en particulier. 

*Exemple:  L'utilisateur authentifié a la permission `inventory.stock.view` valide pour `entreprise-a` à partir de la location `entrepôt-a` seulement. `etagere-r` est une location enfant de entrepot-a.*

* Voir le stock de `etagere-r` => Accès granted

* Voir le stock de la location `boutique-a` (pas un enfant de entrepôt-x) => Permission denied

##### Scope MULTI_LOCATIONS (`access_permission.context = MULTI_LOCATIONS`)

###### Pour une seule compagnie:

La permission s'applique dans un contexte d'entreprise active pour les locations listées.

*Exemple:  L'utilisateur authentifié a la permission `inventory.stock.relocate` valide pour `entreprise-a`  à partir de la location `entrepôt-x` seulement. `product-1` est un produit du catalogue de `entreprise-a`; `etagere-r` et `zone-emballage` sont des locations enfant de entrepot-x.*

- déplacer `product-1` de `etagere-r` à `zone-emballage`  => Accès accordé

- déplacer `product-1` de `etagere-r` à `boutique-a` (pas un enfant de entrepôt-x) => Error Permission denied.
  
  - À noter que l'interface ne devrait pas proposer `boutique-a` mais si une manipulation malvellante était réalisée, le système refuserait le transfert.

- déplacer `product-2` situé dans `boutique-a` => Error Permission denied.

#### Sensibilité

Le concept de sensibilité d'une permission pourrait permettre d'adapter l'UI  et d'ajouter des confirmations d'assignation explicites.

| Sensibilité | Description                                                                                        |
|:----------- |:-------------------------------------------------------------------------------------------------- |
| LOW         | La permissions est générale et a peu d'impact sur le stock ou le system.                           |
| MEDIUM      | La permission a un impact sur la configuration de l'entreprise et/ou la manière de gérer le stock. |
| HIGH        | La permission permet de faire des changements majeurs aux stocks                                   |

##### Sensibilité OWNER-ONLY

La permission ne sera pas créée dans la table `access_permission` car elle n'est pas déléguable. Elle peut être réalisée exclusivement par un utilisteur avec `is_owner=True`.

#### Permission barrée

Cette permission ne sera **PAS** créée car

1. elle est bloquée / impossible pour tous les utilisateurs métier OU
2. elle est listée /  groupée sous un autre nom OU
3. elle est "OWNER-ONLY"

La permission est listée malgré tout dans le référentiel à des fins de documentation.

### 5.1. ![](https://img.shields.io/badge/-App-darkblue.svg) Core (`core.*`)

Centralise les configurations globales du système.

| Code (`codename`)          | Description (`name` / `help_text`)                                                                                                                                                                                                                                                                | Contexte | Sensibilité                                                                 |
|:-------------------------- |:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |:--------:|:---------------------------------------------------------------------------:|
| ~~`core.settings.add`~~    | Ajouter une configuration globale.*La table core.settings ne contient qu'un seul enregistrement.*                                                                                                                                                                                                 | -        | -                                                                           |
| `core.settings.view`       | Consulter les configurations globales                                                                                                                                                                                                                                                             | SYSTEM   | MEDIUM                                                                      |
| `core.settings.change`     | Modifier les configurations globales                                                                                                                                                                                                                                                              | SYSTEM   | HIGH                                                                        |
| ~~`core.settings.delete`~~ | Supprimer les configuration globales.*La table core.settings doit contenir un seul enregistrement.*                                                                                                                                                                                               | -        | -                                                                           |
| ~~`core.image.view`~~      | Voir une image téléversée sur le serveur. Cette permission n'est pas créée car voir une image est associée au modèle correspondant: si l'utilisateur a le droit de voir le modèle, alors il peut aussi voir les images qui lui sont associées.                                                    | -        | -                                                                           |
| `core.image.add`           | Téléverser des images sur le serveur. Le contexte dépend à quel modèle l'image sera associée. Avoir cette permission n'est utile qu'en association de la permission pour gérer le modèle correspondant.<br/>Note: La permission concerne tous les types d'images pouvant être téléversées         | SYSTEM   | MEDIUM<br/>Un utilisteur malveillant pourrait en venir à saturer le serveur |
| `core.image.change`        | Modifier les informations meta d'une image déjà présente sur le serveur. Avoir cette permission n'est utile qu'en association de la permission pour gérer le modèle correspondant.<br/>Note: La permission concerne tous les types d'images pouvant être téléversées                              | SYSTEM   | LOW                                                                         |
| `core.image.delete`        | Supprimer une image téléversée sur le serveur. Le contexte dépend à quel modèle l'image sera associée. Avoir cette permission n'est utile qu'en association de la permission pour gérer le modèle correspondant.<br/>Note: La permission concerne tous les types d'images pouvant être supprimées | SYSTEM   | LOW                                                                         |

### 5.2. ![](https://img.shields.io/badge/-App-darkblue.svg) Users (`users.*`)

Gère les profils utilisateurs et leurs accès.

**Relation hiérarchique entre employés**: Un employé a accès uniquement à tous ses subordonnées (arbre hiérarchique défini par la table users_userhierarchy, un modèle qui utilse MP_Node de django-treebeard)

**Prévention de l'escalade de privilèges**: en tout temps, les permissions pouvant être assignées sont strictement limitées aux permissions détenues par l'utilisateur qui fait l'assignation, sans jamais dépassé son propre périmètre (les `company_id `et `location_id `de ses propres rôles). Un utilisateur ne peut en aucun temps modifier ses propres permissions.

| Code (`codename`)                                                                        | Description (`name` / `help_text`)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | Contexte | Sensibilité |
|:---------------------------------------------------------------------------------------- |:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |:--------:|:-----------:|
| `users.user.add`                                                                         | Créer un nouvel utilisateur dans le système.<br/> - Le champs `is_owner `est invisible, bloqué et fixé à False en tout temps pour un utilisateur qui n'est pas `is_owner=True`.<br/>- L'utilisateur créé sera un subordonné de l'utilisateur "créateur"                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | SYSTEM   | LOW         |
| `users.user.invite`                                                                      | Inviter un utilisateur à créer son propre compte à partir d'un courriel contenant un lien sécurisé                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | SYSTEM   | LOW         |
| `users.user.view`                                                                        | Voir la liste des utilisateurs, incluant leur secteur d'activité<br/><br/>*Un utilisateur avec cette permission ne voit que ses subordonnés.*                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | SYSTEM   | LOW         |
| `users.user.change`                                                                      | Modifier les informations ou préférences d'un utilisateur, excluant le drapeau propriétaire (`user.is_owner`) et incluant leur secteur d'activité<br/><br/>*Un utilisateur avec cette permission ne peut modifier que ses subordonnés.*                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | SYSTEM   | LOW         |
| ~~`users.user.setowner`~~                                                                | Modifier la valeur du champ user.is_owner. *Cette action n'est pas déléguable.*<br/><br/>- Un propriétaire ne peut jamais se révoquer (set `is_owner=false`) lui-même.<br/>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | SYSTEM   | OWNER-ONLY  |
| `users.user.change_own`                                                                  | Modifier les informations et préférences de son propre profil <br/>- Exclut la modification de`user.is_owner`, qui n'est d'ailleurs visible que pour les propriétaires.<br/>- Exclut la modification du superviseur (mais l'info sur le superviseur direct est affiché)                                                                                                                                                                                                                                                                                                                                                                                                                                                              | SYSTEM   | LOW         |
| `users.user.delete`                                                                      | Supprimer un utilisateur (le système refusera si <br/>- il existe au moins une référence à cet utilisateur<br/>- cet utilisteur est `is_owner=True`)<br/><br/>*Un utilisateur avec cette permission ne peut supprimer le compte que de ses subordonnés.*                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | SYSTEM   | MEDIUM      |
| `users.user.setactive`                                                                   | Activer ou désactiver le compte d'un utilisateur (set`user.is_active`)<br/>Cette permission sert à permettre l'activation/désactivation d'un compte sans donner le contrôle total `users.user.change`<br/>*Un utilisateur avec cette permission ne peut changer le statut d'activation que de ses subordonnés.*                                                                                                                                                                                                                                                                                                                                                                                                                      | SYSTEM   | LOW         |
| ~~`users.useractivitysector.view`~~                                                      | Voir les secteurs d'activité. <br/>*Cette permission est incluse dans `users.user.view`*                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |          |             |
| ~~`users.useractivitysector.[<br/>add\|change\|delete]`~~                                | Gérer les secteurs d'activités des utilisateurs<br/>*Ces permissions sont incluses dans `users.user.change`*                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | -        | -           |
| ~~`users.userrole.add`~~<br/>~~`users.userrole.change`~~<br/>~~`users.userrole.delete`~~ | Assigner, modifier ou supprimer les rôles d'un utilisateur. Regroupement sous une seule permission`users.userrole.manage`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | -        | -           |
| `users.userrole.view`                                                                    | Consulter les rôles assignés à une liste d'utilisateurs.<br/><br/>*Un utilisateur avec cette permission ne peut voir les permissions que de ses subordonnés.*                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | SYSTEM   | MEDIUM      |
| `users.userrole.manage`                                                                  | Assigner, modifier ou supprimer les rôles assignés à un utilisateur. <br/><br/>*L'utilisateur avec cette permission est strictement limité <br/>1. Un utilisateur avec cette permission ne peut modifier les permissions que de ses subordonnés. <br/>2. Les permissions pouvant être assignées sont strictement limitées aux permissions détenues par l'utilisateur ayant cette permission (prévention de l'escalade des privilèges).*<br/>L'interface est filtrée pour éviter les erreurs de permissions. Ceci dit, avant l'enregistrement des permissions en DB, les règles sont revérifiées et une erreur de validation est lancée et loguée dans userrolelog si non respectée. Le changement en DB est évidemment non effectué. | SYSTEM   | HIGH        |
| users.userrolelog.view                                                                   | Voir l'historique des modifications sur les assignations de rôle.<br/><br/>*Un utilisateur avec cette permission ne peut voir les informations  concernant que ses subordonnés.*                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | SYSTEM   | MEDIUM      |
| ~~`users.userrolelog.[add\|change\|delete]`~~                                            | `userrolelog `est en lecture seule pour tous (incluant `is_owner=True`)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | -        | -           |

### 5.3. ![](https://img.shields.io/badge/-App-darkblue.svg) Company (`company.*`)

Application permettant de configurer les entreprises, leurs unités de mesure et leurs emplacements [détails ⬀](5-django-apps-and-urls.md#company).

| Code (`codename`)                                      | Description (`name` / `help_text`)                                                                                                                                                                                                                                                                                                        | Contexte | Sensibilité |
|:------------------------------------------------------ |:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |:--------:|:-----------:|
| `company.company.view`                                 | Voir les informations de configuration de l'entreprise.                                                                                                                                                                                                                                                                                   | COMPANY  | MEDIUM      |
| ~~`company.company.add`~~                              | Créer une nouvelle entreprise. Cette action n'est pas déléguable.                                                                                                                                                                                                                                                                         | SYSTEM   | OWNER-ONLY  |
| ~~`company.company.change`~~                           | Modifier les informations de l'entreprise. Cette action n'est pas déléguable.                                                                                                                                                                                                                                                             | COMPANY  | OWNER-ONLY  |
| ~~`company.company.archive`~~                          | Archiver ou désarchiver l'entreprise<br/>Une entreprise archivée `(is_archive = True`) n'est plus disponible pour aucune action (création de produit, modification d'inventaire, etc) et n'apparaît plus dans le tableau de bord et les rapports consolidés [Est en consultation seulement]. <br/><br/>Cette action n'est pas déléguable. | COMPANY  | OWNER-ONLY  |
| ~~`company.company.delete`~~                           | Supprimer une entreprise.  Cette action est irréversible et supprime l'entreprise, toutes les références et tout l'historique associé à l'entreprise. Tous les rôles associés à l'entreprises et toutes les assignations de rôle limitées à cette entreprise sont également supprimées.<br/><br/>Cette action n'est pas déléguable.       | COMPANY  | OWNER-ONLY  |
| ~~`company.locationtype.[view, add, change, delete]`~~ | Voir, ajouter, modifier ou supprimer les types de location.<br/>*Géré  par `company.locationtype.manage`*                                                                                                                                                                                                                                 | -        | -           |
| `company.locationtype.manage`                          | Gérer les types de location (voir, ajouter, modifier et supprimer)                                                                                                                                                                                                                                                                        | COMPANY  | MEDIUM      |
| `company.location.view`                                | Consulter les emplacements                                                                                                                                                                                                                                                                                                                | COMPANY  | LOW         |
| ~~`company.location.main.[add\|change\|delete]`~~      | Créer, modifier ou supprimer un emplacement de haut niveau (emplacement racine) <br/><br/>Cette action n'est pas déléguable.                                                                                                                                                                                                              | COMPANY  | OWNER-ONLY  |
| ~~company.location.sub.view~~                          | Géré par company.location.view (sans distinction entre "main" ou "sub")                                                                                                                                                                                                                                                                   | -        | -           |
| ~~`company.location.sub.[add\|change\|delete]`~~       | Créer, modifier ou supprimer un sous-emplacement (emplacement qui a nécessairement un parent)<br/><br/>Actions regroupées sous le libellé `company.location.sub.manage`                                                                                                                                                                   | -        | -           |
|                                                        |                                                                                                                                                                                                                                                                                                                                           |          |             |
| `company.location.sub.manage`                          | Gérer les sous-locations (emplacements enfants). À la création / mise à jour, le système doit vérifier que le parent choisi appartient bien à la même entreprise. Aussi, le système empêchera la suppression si des références (stock) y font référence.                                                                                  | COMPANY  | MEDIUM      |
| `company.uom.view`                                     | Consulter toutes les unités de mesure définies dans l'entreprise                                                                                                                                                                                                                                                                          | COMPANY  | LOW         |
| `company.uom.manage`                                   | Gérer toutes les unités de mesure utilisées dans l'entreprise.                                                                                                                                                                                                                                                                            | COMPANY  | HIGH        |
| ~~company.import~~                                     | Importer massivement les données d'une entreprise, incluant les infos de locations, le catalogue et l'inventaire (CSV).<br/><br/>Le système ajoute les données aux données déjà existantes. Habituellement fait sur une entreprise nouvelle créée.                                                                                        | COMPANY  | OWNER-ONLY  |
| ~~company.export~~                                     | Exporter les données d'une entreprise, incluant les infos de locations, le catalogue et l'inventaire (CSV).                                                                                                                                                                                                                               | COMPANY  | OWNER-ONLY  |

### 5.4. ![](https://img.shields.io/badge/-App-darkblue.svg) Catalogue (`catalogue.*`)

Application gérant le référentiel des produits, leurs déclinaisons (variantes), leur classification (catégories), leurs images, leur conditionnement (packaging) et leurs caractéristiques techniques [détails ⬀](5-django-apps-and-urls.md#catalogue).

| Code (`codename`)                                                 | Description (`name` / `help_text`)                                                                                                                                                                                                                                                                                                            | Contexte | Sensibilité |
|:----------------------------------------------------------------- |:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |:--------:|:-----------:|
| `catalogue.product.view`                                          | Consulter le catalogue des produits (inclut les infos des modèles de produit, leurs variantes. leurs catégories, leurs images associées et leur conditionnement. Exlut les infos de configuration).                                                                                                                                           | COMPANY  | LOW         |
| `catalogue.product.add`                                           | Créer un nouveau produit (inclut les modèles de produit, leurs variantes. leurs catégories, leurs images associées et leur conditionnement. Exclut l'archivage.                                                                                                                                                                               | COMPANY  | MEDIUM      |
| `catalogue.product.change`                                        | Modifier les caractéristiques d'une  fiche produit (inclut les modèles de produit, leurs variantes. leurs catégories, leurs images associées et leur conditionnement. Exclut l'archivage.                                                                                                                                                     | COMPANY  | MEDIUM      |
| `catalogue.product.archive`                                       | Archiver ou désarchiver un produit.<br/>- Un produit archivé n'apparaît plus dans les listes de produits ni dans les recherches<br/>- *Un modèle archivé va archiver toutes ses variantes. Une variante archivée n'affecte pas son modèle ni les autres variante.* <br/>- Le système bloquera l'archivage si du stock existe pour ce produit. | COMPANY  | HIGH        |
| `catalogue.product.delete`                                        | Supprimer définitivement un produit du catalogue de l'entreprise. *Le système bloquera la suppression si des référence au produit existe.*                                                                                                                                                                                                    | COMPANY  | HIGH        |
| `catalogue.category.view`                                         | Consulter l'arborescence complète des catégories.                                                                                                                                                                                                                                                                                             | COMPANY  | LOW         |
| ~~`catalogue.category.[add\|change\|delete]`~~                    | Ajouter, modifier ou supprimer une catégorie. <br/><br/>Géré par `catalogue.category.manage`                                                                                                                                                                                                                                                  | -        | -           |
| `catalogue.category.manage`                                       | Gérer les catégories. Le système bloquera la suppression d'une catégorie référencée.                                                                                                                                                                                                                                                          | COMPANY  | MEDIUM      |
| `catalogue.attribute.manage`                                      | Gérer les attributs (clé et valeurs) de variantes de produit dans un module dédié aux attributs, indépendemment des produits et leur assignation aux-dits attributs                                                                                                                                                                           | COMPANY  | HIGH        |
| ~~view\|add\|create\|delete direct sur les modèles de catalogue~~ | Toutes les autres permissions CRUD directes sur les modèles (`ProducModel`, `ProductConfig`, `ProductPackaging`, `ProductAttribute`, `ProducImage`, `ProductModelImage`) sont gérées avec les permissions sur `Product`: un utilisateur ayant le droit de modifier un produit peut modifier toutes ses caractéristiques.                      | -        | -           |

### 5.5. ![](https://img.shields.io/badge/-App-darkblue.svg) Inventory (`inventory.*`)

Application gérant l'état des stocks physiques, la traçabilité des lots et l'historique complet des mouvements de marchandises.

| Code (`codename`)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Description (`name` / `help_text`)                                                                                                                                                                                                              | Contexte        | Sensibilité |
|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |:---------------:|:-----------:|
| `inventory.stock.view`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | Consulter les quantité   de stock disponibles.                                                                                                                                                                                                  | LOCATION        | MEDIUM      |
| ~~`inventory.stock.[add\|change\|delete]`~~                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Ajouter/modifier/supprimer du stock en inventaire.<br/><br/>Actions impossible de cette manière: les permissions sont plus pointues et permettent de préciser la manière et les raisons pour modifier le stock.                                 | -               | -           |
| `inventory.movement.view`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Consulter le journal historique des mouvements de stock. Permet de rechercher et filter.                                                                                                                                                        | COMPANY         | LOW         |
| ~~`inventory.movement.[add\|change\|delete]`~~                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Actions impossibles car il s'agit d'un journal d'historique en lecture seule (même pour `is_owner=True`)                                                                                                                                        | -               | -           |
| ~~`inventory.movementreason.[view\|add\|change\|delete]`~~                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Voir, ajouter, modifier ou supprimer. Action impossible de cette manière: utilise `manage`.                                                                                                                                                     | -               | -           |
| `inventory.movementreason.manage`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Gérer les raisons pour modifier les quantités en inventaire. Permet d'associer la permission requise à la raison.                                                                                                                               | COMPANY         | HIGH        |
| <a id="permissions-reasons"></a>`inventory.stock.increase`<br/>`inventory.stock.decrease`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Augmenter ou diminuer l'inventaire (permissions génériques)<br/><br/>Cette permission générique est créée par flexibilité avec le système de movementreason personnalisé, au cas où aucune des autres permissions plus précise de conviendrait. | LOCATION        | HIGH        |
| `inventory.stock.purchase`<br/>*Ex: T-Shirt d'un fournisseur est reçu dans la zone de réception de marchandises.*<br/>*- stock.quantity est augmenté*<br/>*- un movement est créé avec location_source NULL et location_dest qui pointe vers la location modifiée.*                                                                                                                                                                                                                                                                                                                                                                                                                   | Augmenter l'inventaire en raison d'une commande d'achat à un fournisseur.                                                                                                                                                                       | LOCATION        | MEDIUM      |
| `inventory.stock.manufacture`<br/>*Ex: T-Shirt sort de la fabrique et est stocké dans l'entrepôt.*<br/>*- stock.quantity est augmenté*<br/>*- un movement est créé avec location_source NULL et location_dest qui pointe vers la location modifiée.                                                                                                                                                                                                                                                                                                                                                                                                                                   | Augmenter l'inventaire en raison de l'arrivée de produits issues d'une chaîne de production interne.                                                                                                                                            | LOCATION        | MEDIUM      |
| `inventory.stock.sale`<br/>*Ex: T-Shirt est vendu.*<br/>*- stock.quantity est diminué*<br/>*- un movement est créé avec location_source pointant vers la location modifié et location_dest NULL.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Diminuer l'inventaire en raison d'une vente.                                                                                                                                                                                                    | LOCATION        | MEDIUM      |
| `inventory.stock.count_more`<br/>*Ex: Le nombre de T-Shirt sur l'étagère A est plus élevé que la quantité indiquée en inventaire.*<br/>*- stock.quantity est augmenté*<br/>*- un movement est créé avec location_source et location_dest pointant vers la location modifiée.*                                                                                                                                                                                                                                                                                                                                                                                                         | Augmenter l'inventaire en raison d'un ajustement de décompte d'inventaire.                                                                                                                                                                      | LOCATION        | MEDIUM      |
| `inventory.stock.count_less`<br/>*Ex: Le nombre de T-Shirt sur l'étagère B est plus basse que la quantité indiquée en inventaire.*<br/>*- stock.quantity est diminué*<br/>*- un movement est créé avec location_source et location_dest pointant vers la location modifiée.*                                                                                                                                                                                                                                                                                                                                                                                                          | Diminuer l'inventaire en raison d'un ajustement de décompte d'inventaire.                                                                                                                                                                       | LOCATION        | MEDIUM      |
| `inventory.stock.loss`<br/>*Ex: Un T-Shirt sur l'étagère C est déchiré et donc retiré du stock courant.*<br/>*- stock.quantity est diminué*<br/>*- un movement est créé avec location_source pointant vers la location modifié et location_dest est NULL.*                                                                                                                                                                                                                                                                                                                                                                                                                            | Diminuer l'inventaire en raison de marchandises perdues (bris, vol, date de péremption dépassé, etc).                                                                                                                                           | LOCATION        | MEDIUM      |
| `inventory.stock.uom_pack`<br/>*Ex: 10 T-Shirt sont retirés de la tablette et placer dans une boîte pour une vente par pack plutôt que unitaire.*<br/>*- stock.quantity avec uom unit unit est diminué* <br/>*- stock.quantity avec uom unit pack est augmenté* <br/>*- un movement est créé avec location_source du premier changement et location_dest du deuxième changement. quantity_delta est 0.*                                                                                                                                                                                                                                                                               | Diminuer l'inventaire en raison d'un changement d'unité de mesure.                                                                                                                                                                              | LOCATION        | MEDIUM      |
| `inventory.stock.uom_unpack`<br/>*Ex: 10 T-Shirt sont retirés d'une boîte de fournisseur et placer sur la tablette pour renflouer l'emplacement.*<br/>*- stock.quantity avec uom unit parck est augmenté* <br/>*- stock.quantity avec uom unit unit est diminué* <br/>*- un movement est créé avec location_source du premier changement et location_dest du deuxième changement. quantity_delta est 0.*                                                                                                                                                                                                                                                                              | Augmenter l'inventaire en raison d'un changement d'unité de mesure.                                                                                                                                                                             | LOCATION        | MEDIUM      |
| `inventory.stock.relocate`<br/>*Ex: 1 T-Shirt est déplacé de l'emplacement Tablette A et placé dans l'emplacement  Lift 12.*<br/>*- stock.quantity de Tablette A est diminué* <br/>*- stock.quantity de Lift 12 est augmenté* <br/>*- un movement est créé avec location_source du premier changement et location_dest du deuxième changement. quantity_delta est 0.*                                                                                                                                                                                                                                                                                                                 | Diminuer l'inventaire pour le relocaliser dans un emplacement ayant le même parent principal.                                                                                                                                                   | MULTI_LOCATIONS | MEDIUM      |
| `inventory.stock.transfer_out`<br/>*Ex: 10 T-Shirt sont retirés de l'emplacement Zone Emballage de l'Entrepôt X pour être envoyés à Boutique ABC. Boutique ABC et Entrepôt X sont deux emplacements de haut niveau de la même entreprise. <br/>- Dans stock: qty est diminué de 10.<br/>- Dans movement: nouvelle entrée avec location_source pointant vers la Zone d'emballage de Entrepôt X et location_destination est NULL<br/>- Dans transit: nouvelle entrée avec les mêmes company_id (source et dest) et uom_id (source et dest). location_source_id pointe vers Entrepôt X, location_dest_id pointe vers Boutique ABC, quantity_received est NULL et is_complete est False.* | Diminuer l'inventaire pour l'envoyer dans un emplacement ayant un parent principal différent                                                                                                                                                    | LOCATION        | MEDIUM      |
| `inventory.stock.transfer_in`<br/>*Ex: 10 T-Shirt sont réceptionnés à Boutique ABC à partir du transit barcode (ou en sélectionnant la ligne du produit après avoir ouvert transit. <br/><br/>- Dans transit: entrée est mise à jour avec info du destinataire et, qté reçue et est marqué comme complété.* <br/>- Dans stock: qty est augmenté de 10.<br/>- Dans movement: nouvelle entrée avec location_source NULL et location_destination pointe vers Boutique ABC<br/>                                                                                                                                                                                                           | Augmenter l'inventaire pour l'envoyer dans un emplacement ayant un parent principal différent                                                                                                                                                   | LOCATION        | MEDIUM      |
| `inventory.stock.intercompany_out`<br/>*Ex: 10 T-Shirt sont retirés de l'emplacement Zone Emballage de l'Entrepôt X pour être envoyés à Entreprise Z. Entrepôt X et Entreprise Z sont deux entreprises indépendantes appartenant au même propriétaire <br/>- Dans stock: qty est diminué de 10.<br/>- Dans movement: nouvelle entrée avec location_source pointant vers la Zone d'emballage de Entrepôt X et location_destination est NULL<br/>- Dans transit: nouvelle entrée avec les infos de source et company_dest pointant vers Entreprise Z. location_dest, uom_dest et quantity_received sont NULL. is_complete est False.*                                                   | Diminuer l'inventaire en raison d'une vente interne vers une entreprise du même propriétaire.                                                                                                                                                   | LOCATION        | MEDIUM      |
| `inventory.stock.intercompany_in`<br/>*Ex: 10 T-Shirt sont réceptionnés à Entrepôt X à partir du transit barcode (ou en sélectionnant la ligne du produit après avoir ouvert la liste des transit. <br/>Dans transit: qté reçue et uom_dest sont mis à jour et is_completed est passé à True.* <br/>*- Dans stock: qty est augmenté de 10.*<br/>*- Dans movement: nouvelle entrée avec location_source NULL et location_destination pointe vers Entrepôt X (ou un emplacement interne d'Entrepôt X)*                                                                                                                                                                                  | Augmenter l'inventaire en raison de l'achat (la réception) interne de stock d'une entreprise du même propriétaire.                                                                                                                              | LOCATION        | MEDIUM      |

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

| Code (`codename`)                     | Description (`name` / `help_text`)                                         | Contexte        | Sensibilité |
|:------------------------------------- |:-------------------------------------------------------------------------- |:---------------:|:-----------:|
| ~~`reporting.[add\|change\|delete]`~~ |                                                                            |                 |             |
| reporting.multicompany.view           | Lecture des rapports rassemblant les données de plusieurs entreprises      | MULTI_COMPANIES | HIGH        |
| `reporting.stock_levels.view`         | Lecture des rapports de rotations, ruptures imminentes et seuils d'alerte. | MULTI_COMPANIES | HIGH        |
| reporting.stock_level.view            |                                                                            |                 |             |

### 5.7. ![](https://img.shields.io/badge/-App-darkblue.svg) Access (`acces.*`)

Configure les rôles de l'application

| Code (`codename`)                                                                                               | Description (`name` / `help_text`)                                                                                                                                                          | Contexte | Sensibilité |
|:--------------------------------------------------------------------------------------------------------------- |:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |:--------:|:-----------:|
| ~~`access.permission.[add\|change\|delete]`~~                                                                   | Changer les  informations de la table des permissions.*Impossible car chaque permission est associée à un comportement d'accessibilité codé en dur.*                                        | -        | -           |
| ~~`access.permission.view`~~                                                                                    | Voir les informations de la table des permissions. Jamais parce que la permission`access.manage` implique nécessairement un accès en lecture et un accès en lecture seul n'a pas d'utilité. | -        | -           |
| ~~`access.role.[view\|create\|change\|delete]`~~ et ~~`access.rolepermissions.[view\|create\|change\|delete]`~~ |                                                                                                                                                                                             | -        | -           |
| `accces.manage`                                                                                                 | Gérer les rôles et leur association avec des permissions                                                                                                                                    | SYSTEM   | HIGH        |

---

## <a id="roles"></a>Rôles par Défaut

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

## Plan de tests <a id="tests"></a>

Les tests de sécurité doivent couvrir au minimum :

- un propriétaire peut accéder à toutes les compagnies ;
- un propriétaire ne voit que la compagnie courante dans une vue `/c/<company_slug>/...` ;
- un employé ne peut accéder qu'aux compagnies autorisées ;
- un employé ne peut pas accéder aux vues multi-companies`/mc/...` ;
- un employé autorisé peut créer un autre employé ;
- un employé ne peut pas créer, modifier ou désactiver un propriétaire ;
- il est impossible de désactiver le dernier propriétaire actif ;
- il est impossible d'obtenir un état sans propriétaire actif ;
- les modèles company-scoped ne retournent jamais des données hors scope courant ;
- les vues owner-only sont explicitement protégées par `is_owner=True`.

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
- employé de A ne peut pas accéder à /mc/...;
- employé multi-company peut accéder à A (/c/company-a/...) et B (/c/company-b/) ;
- employé avec location limitée ne voit pas les autres locations ;
- employé sans permission stock ne peut pas modifier stock.

### Tests context

- sur /c/company-a/..., même owner voit par défaut les données de A seulement ;
- sur /mc/..., seulement owner peut utiliser les querysets globaux ;
- sans contexte explicite, les requêtes échouent.

## Extension des Tests de Sécurité (Couverture Matrice RBAC)

#### Tests de validation de la Matrice RBAC

##### 1. Cas d'usage : Permissions de type "Compagnie & Lieu" (`context = True`)

Ces tests vérifient le comportement des droits métier spécifiques à une entité (ex: `catalogue.product.delete`).

###### Cas 1.1 : Permission Globale / Rôle Global / Assignation Globale

- **Données DB :** `perm.company_id = NULL`, `userrole.company_id = NULL`, `userrole.location_id = NULL`
- **Test :** L'employé peut exécuter l'action sur la Compagnie A (Lieu X) **ET** sur la Compagnie B (Lieu Y).
- **Résultat attendu :** Succès partout.

###### Cas 1.2 : Permission Globale / Rôle Global / Assignation Restreinte (Compagnie seule)

- **Données DB :** `perm.company_id = NULL`, `userrole.company_id = company-a`, `userrole.location_id = NULL`
- **Test A :** L'employé tente l'action sur la Compagnie A. *(Attendu : Succès)*
- **Test B :** L'employé tente l'action sur la Compagnie B. *(Attendu : Échec / 403 Forbidden)*

###### Cas 1.3 : Permission Globale / Rôle Global / Assignation Restreinte (Compagnie + Lieu)

- **Données DB :** `perm.company_id = NULL`, `userrole.company_id = id de company-a`, `userrole.location_id = Entrepot_Paris`
- **Test A (Même Lieu) :** Action demandée sur la Compagnie A au lieu `Entrepot_Paris`. *(Attendu : Succès)*
- **Test B (Lieu Enfant) :** Action demandée sur la Compagnie A au lieu `Allee_01_Paris` (enfant direct de `Entrepot_Paris`). *(Attendu : Succès)*
- **Test C (Lieu Parent ou Cousin) :** Action demandée sur la Compagnie A au lieu `Siege_Lyon` ou au niveau racine de la compagnie. *(Attendu : Échec / 403)*
- **Test D (Autre Compagnie) :** Action demandée sur la Compagnie B au lieu `Entrepot_Paris`. *(Attendu : Échec / 403)*

###### Cas 1.4 : Permission Spécifique (Rôle lié à une Compagnie) / Assignation Globale

- **Données DB :** `perm.company_id = id de company-a`, `userrole.company_id = NULL`, `userrole.location_id = NULL`
- **Test A :** L'employé tente l'action sur la Compagnie A. *(Attendu : Succès - l'entonnoir valide la Compagnie A)*
- **Test B :** L'employé tente l'action sur la Compagnie B. *(Attendu : Échec / 403 - car la permission elle-même est exclusive à A)*

###### Cas 1.5 : Permission Spécifique (Rôle lié à une Compagnie) / Assignation Restreinte (Même Compagnie)

- **Données DB :** `perm.company_id = id de company-a`, `userrole.company_id = id de company-a`, `userrole.location_id = NULL`
- **Test :** L'employé tente l'action sur la Compagnie A.
- **Résultat attendu :** Succès.

###### Cas 1.6 : Permission Spécifique / Assignation Restreinte (Même Compagnie + Lieu)

- **Données DB :** `perm.company_id = id de company-a`, `userrole.company_id = id de company-a`, `userrole.location_id = Entrepot_Paris`
- **Test A (Lieu Exact) :** Action demandée sur la Compagnie A à `Entrepot_Paris`. *(Attendu : Succès)*
- **Test B (Lieu Enfant) :** Action demandée sur la Compagnie A à `Allee_01_Paris`. *(Attendu : Succès)*
- **Test C (Lieu Hors Scope) :** Action demandée sur la Compagnie A à `Entrepot_Marseille`. *(Attendu : Échec / 403)*

###### Cas 1.7 : Permission Spécifique / Assignation Restreinte (Compagnie différente) -> Conflit

- **Données DB :** `perm.company_id = id de company-a`, `userrole.company_id = id de company-a`, `userrole.location_id = NULL`
- **Test :** L'employé tente l'action sur la Compagnie A (ou la Compagnie B).
- **Résultat attendu :** Échec / 403 partout *(Conflit de configuration en base de données)*.

---

##### 2. Cas d'usage : Permissions de type "Global" (`need_globalcontext = True`)

Ces tests ciblent les actions d'administration système ne dépendant pas d'une entité commerciale (ex: `core.settings.change`).

###### Cas 2.1 : Permission Globale / Assignation Totalement Globale

- **Données DB :** `perm.company_id = NULL`, `userrole.company_id = NULL`, `userrole.location_id = NULL`
- **Test :** L'utilisateur tente d'accéder à la configuration système globale sur une route `/g/...` sans spécifier de compagnie.
- **Résultat attendu :** Succès.

###### Cas 2.2 : Permission Globale / Assignation Restreinte à une Compagnie

- **Données DB :** `perm.company_id = NULL`, `userrole.company_id = id de company-a`, `userrole.location_id = NULL`
- **Test :** L'utilisateur tente d'accéder à l'action globale.
- **Résultat attendu :** Échec / 403 *(Un droit global ne peut être exercé par un utilisateur dont le rôle est cloisonné à une filiale)*.

###### Cas 2.3 : Permission Globale / Assignation Restreinte à un Lieu

- **Données DB :** `perm.company_id = NULL`, `userrole.company_id = NULL`, `userrole.location_id = Entrepot_Paris`
- **Test :** L'utilisateur tente d'accéder à l'action globale.
- **Résultat attendu :** Échec / 403 *(Même logique, restriction trop sévère pour du global)*.

---

##### Tests des Limites et Robustesse (Edge Cases)

Validation des paramètres de la fonction de service

- **Test Absence de Contexte Compagnie :** Appeler la méthode `has_perm()` pour une permission de type `need_companycontext=True` en passant `context_company_id=None`. *(Attendu : Retourne `False` immédiatement).*
- **Test Lieu Inexistant / Supprimé :** L'utilisateur possède un `userrole.location_id = 9999` qui a été supprimé de la base de données entre-temps. L'appel doit intercepter l'erreur `DoesNotExist` proprement. *(Attendu : Retourne `False` sans faire crasher l'application).*
- **Test Boucle Multi-Rôles (Cumul des droits) :** L'utilisateur possède deux rôles distincts :
  - Le Rôle 1 l'autorise sur la Compagnie A (Lieu exact `Paris`).
  - Le Rôle 2 l'autorise sur la Compagnie A (Lieu exact `Lyon`).
  - **Test :** L'utilisateur demande l'accès pour la Compagnie A à `Lyon`. Le système doit analyser le Rôle 1 (qui échoue), continuer la boucle, analyser le Rôle 2 et enfin accorder l'accès. *(Attendu : Retourne `True`)*.

### Test natif de Django pour `user.has_perm`

L'intégration native dans `user.has_perm` simplifie l'écriture des tests car il est possible d'utiliser le test natif de Django (`django.test.Client`) ou simuler les requêtes en alimentant manuellement votre conteneur `CompanyContext` lors du `setUp` de vos tests.

Pour tester le cloisonnement, la configuration actuelle est idéale :

1. Les tests simuleront des requêtes sur les URLs .
2. Le `CompanyMiddleware` s'exécutera.
3. Le `CompanyContext` sera alimenté.
4. `user.has_perm()` interceptera la bonne compagnie sans aucune plomberie additionnelle.

---
