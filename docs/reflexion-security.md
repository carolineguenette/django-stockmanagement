# Réflexion sur l'architecture de sécurité et le cloisonnement des données

Document de synthèse de l'atelier du 13–14 août 2026.

> **Statut : décision d'architecture, avant implémentation.**
> 
> Les exemples de code de ce document illustrent l'architecture cible. Ils ne
> décrivent pas nécessairement l'état actuel du code et devront être validés par
> des tests avant leur intégration.

Ce document complète notamment :

- [`2-conception.md`](2-conception.md) ;
- [`4-data-security.md`](4-data-security.md) ;
- [`5-django-apps-and-urls.md`](5-django-apps-and-urls.md) ;
- [`6-database-models.md`](6-database-models.md).

---

## 1. Séparer contexte, cloisonnement, autorisation et règles métier

### Réflexion / options envisagées

Le premier modèle envisagé donnait beaucoup de responsabilités au
`CompanyContextMiddleware` : identifier la compagnie, vérifier son existence,
vérifier l'accès de l'utilisateur et alimenter les managers filtrants.

Cette approche mélange toutefois quatre questions différentes :

1. **Contexte de la requête** : quelle compagnie ou quel mode de navigation la
   requête vise-t-elle ?
2. **Cloisonnement des données** : quelles lignes une requête ORM peut-elle
   retourner ?
3. **Autorisation RBAC** : l'utilisateur peut-il effectuer une action donnée
   dans le périmètre demandé ?
4. **Invariant métier** : l'état courant permet-il cette action, par exemple
   une écriture dans une compagnie archivée ?

Une autre possibilité aurait été de représenter directement dans le middleware
les six contextes de permissions (`SYSTEM`, `DELEGATE`, `COMPANY`,
`MULTI_COMPANIES`, `LOCATION`, `MULTI_LOCATIONS`). Ces valeurs décrivent
cependant la sémantique des permissions, et non le mode fondamental d'accès aux
données.

### Décision finale

Les responsabilités sont séparées :

| Question                              | Composant principal                         |
| ------------------------------------- | ------------------------------------------- |
| Quelle compagnie est demandée ?       | application `scope`, middleware et contexte |
| Quelles lignes l'ORM peut-il lire ?   | managers/querysets de l'application `scope` |
| L'action est-elle autorisée ?         | backend RBAC de l'application `access`      |
| Quelles compagnies sont accessibles ? | `CompanyAccessService`                      |
| L'opération métier est-elle valide ?  | service métier de l'application concernée   |
| La base demeure-t-elle cohérente ?    | validations de modèles et contraintes SQL   |

Les six contextes RBAC sont conservés dans `access`, mais ne deviennent pas six
types de managers ou six modes de middleware.

`LOCATION` et `MULTI_LOCATIONS` raffinent un accès mono-compagnie.
`DELEGATE` décrit une capacité de délégation. `SYSTEM` concerne une action
globale. Aucun de ces trois concepts ne doit, à lui seul, changer le manager ORM
utilisé.

---

## 2. Types de scopes de requête

### Réflexion / options envisagées

Un `CompanyContext` limité à un entier est suffisant pour le POC initial, mais
il représente difficilement la différence entre :

- une route mono-compagnie ;
- une route multi-compagnies ;
- une route globale qui ne doit pas utiliser implicitement une compagnie ;
- l'absence accidentelle de contexte.

Une liste de compagnies aurait pu être placée dans le même `ContextVar` pour les
routes `/mc/`. Cette liste dépend toutefois de l'utilisateur, de la permission,
des filtres demandés et de l'état des compagnies. La rendre ambiante augmenterait
le risque d'utiliser un périmètre implicite ou périmé.

### Décision finale

Les modes conceptuels retenus sont :

```text
UNSCOPED
COMPANY(company_id, is_active)
MULTI_COMPANIES
```

Le contexte mono-compagnie peut être enrichi avec des informations stables et
utiles, notamment `company_id` et `is_active`. Il ne contient pas les
permissions de l'utilisateur.

En mode multi-compagnies, la liste autorisée n'est pas placée automatiquement
dans le `ContextVar`. Elle est calculée par un service puis transmise
explicitement au queryset.

Exemple cible possible :

```python
# Application : scope
# Fichier pressenti : src/scope/context.py

from dataclasses import dataclass
from enum import Enum


class ScopeMode(Enum):
    UNSCOPED = "unscoped"
    COMPANY = "company"
    MULTI_COMPANIES = "multi_companies"


@dataclass(frozen=True)
class RequestScope:
    mode: ScopeMode
    company_id: int | None = None
    company_is_active: bool | None = None
```

Le détail de cette classe demeure à finaliser au moment de l'implémentation.

---

## 3. Structure des URLs

### Réflexion / options envisagées

Deux architectures ont été comparées.

**Compagnie dans la session** : des URLs courtes comme `/products/t-shirt/`
auraient utilisé une compagnie active stockée en session. Cette solution est
agréable pour les employés n'ayant accès qu'à une compagnie, mais rend l'URL
ambiguë. Elle crée surtout un risque avec plusieurs onglets : changer la
compagnie dans un onglet change la session utilisée par tous les autres.

**Compagnie dans l'URL** : `/c/<company_slug>/...` rend le périmètre explicite,
stable et testable. Le slug ne constitue pas une autorisation ; un utilisateur
peut le modifier, mais le RBAC doit alors refuser l'accès.

### Décision finale

Les familles de routes retenues sont :

```text
/c/<company_slug>/...  vues mono-compagnie
/mc/...                vues et rapports multi-compagnies
/g/...                 vues globales/système
/admin/...             administration technique Django
```

Les routes d'authentification et autres routes réellement hors compagnie
restent également possibles sans préfixe company-scoped.

Même un propriétaire consultant `/c/acme/...` reste limité aux données d'Acme.
Le statut `is_owner` n'élargit jamais implicitement une vue mono-compagnie.

Le sélecteur de compagnie dans l'interface redirige vers la route équivalente
sous un autre slug. Pour un utilisateur n'ayant accès qu'à une compagnie, ce
sélecteur peut être masqué.

---

## 4. Responsabilités du middleware

### Réflexion / options envisagées

Le middleware actuel détecte `/c/<slug>/` avec une expression régulière. Cette
solution installe très tôt le contexte et peut court-circuiter la requête.

L'alternative consiste à utiliser la résolution d'URL de Django dans
`process_view()`. À ce moment, `resolver_match` et `view_kwargs` sont
disponibles, mais la vue, son `dispatch()` et ses mixins n'ont pas encore été
appelés. Cette solution évite de dupliquer la syntaxe de l'URL dans une regex.

Le middleware aurait aussi pu vérifier les permissions ou calculer les
compagnies accessibles. Cela lui donnerait trop de responsabilités et
couplerait le routage au RBAC.

### Décision finale

Le middleware mono-compagnie doit :

1. reconnaître une route `/c/<company_slug>/...` ;
2. résoudre la compagnie avec le manager normal du modèle `Company` ;
3. retourner `404` si le slug n'existe pas ;
4. attacher la compagnie à `request` ;
5. installer un contexte immuable dans un `ContextVar` ;
6. restaurer le contexte précédent dans un bloc `finally`.

Il ne doit pas :

- vérifier les permissions métier ;
- calculer les locations autorisées ;
- calculer les compagnies autorisées ;
- accorder un accès global à un propriétaire ;
- remplacer les services métier.

La résolution et l'autorisation produisent des réponses distinctes :

```text
slug inexistant                    → 404 Not Found
compagnie existante mais interdite → 403 Forbidden
action métier interdite            → 403 Forbidden
```

L'utilisation de `process_view()` est privilégiée comme architecture cible
afin d'éviter la duplication entre URLconf et regex. La regex actuelle peut
rester une étape raisonnable du POC jusqu'à la révision du middleware.

Exemple de structure, à adapter soigneusement pour garantir le nettoyage du
`ContextVar` :

```python
# Application : scope
# Fichier pressenti : src/scope/middleware.py

class ContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.scope_token = None
        try:
            return self.get_response(request)
        finally:
            reset_request_scope(request.scope_token)

    def process_view(self, request, view_func, view_args, view_kwargs):
        company_slug = view_kwargs.get("company_slug")
        if company_slug is None:
            return None

        company = Company.objects.filter(slug=company_slug).first()
        if company is None:
            raise Http404("Company not found.")

        request.company = company
        request.scope_token = set_company_scope(company)
        return None
```

Ce squelette n'est pas une implémentation finale : la classification explicite
des namespaces `/c/`, `/mc/` et `/g/`, l'ordre des middlewares et les cas de
résolution doivent être testés.

---

## 5. `404`, `403` et validation de l'accès à une compagnie

### Réflexion / options envisagées

Résoudre une compagnie ne signifie pas que l'utilisateur peut y accéder. À
l'inverse, demander au manager d'un modèle comme `Product` de déterminer si le
slug existe mélangerait résolution de route et filtrage ORM.

Posséder n'importe quel rôle actif pourrait servir de critère d'entrée, mais
cela risque d'être trop permissif, notamment pour un rôle spécial de type
`DELEGATE`.

### Décision finale

Le modèle `Company` utilise un manager global normal. Le middleware s'en sert
pour résoudre le slug et produire le `404` avant l'appel de la vue.

Une vérification distincte produit le `403` lorsque l'utilisateur ne peut pas
entrer dans la compagnie. Le critère exact d'« accès minimal à une compagnie »
reste à formaliser : permission de consultation dédiée, permission exigée par
la vue, ou service d'accès spécifique.

Le backend `src/access/auth_backend.py` demeure responsable de
`user.has_perm(...)`. Il est encore en développement et devra être revu avec
les règles multi-compagnies décrites plus bas.

---

## 6. Managers des modèles entièrement company-scoped

### Réflexion / options envisagées

Le manager filtrant par défaut protège contre le classique oubli suivant :

```python
Product.objects.all()
```

Un accès global implicite pour `manage.py`, `pytest` ou l'admin a été envisagé
et se trouve dans le POC actuel. La détection fondée sur `sys.argv` ou
l'inspection de la pile d'appel est difficile à auditer et peut ouvrir une
porte globale selon le contexte d'exécution.

Un seul manager non filtré pourrait servir aux vues multi-compagnies, mais un
appel accidentel à `.all()` recréerait le risque de fuite.

### Décision finale

Les modèles entièrement rattachés à une compagnie utilisent, dans cet ordre :

```python
# Applications : company, catalogue et inventory
# Exemple : src/catalogue/models/product.py

objects = CompanyScopedManager()
companies = CompaniesScopedManager()
unscoped = UnscopedManager()
```

Signification :

- `objects` : accès normal et mono-compagnie, fermé par défaut ;
- `companies` : accès multi-compagnies exigeant une liste explicite ;
- `unscoped` : accès non filtré, réservé à l'infrastructure technique.

Le manager normal et sûr demeure le `_default_manager`. Le manager technique
ne doit pas être placé en premier uniquement pour faciliter l'admin.

Exemple de configuration explicite possible :

```python
# Application : catalogue
# Fichier d'un modèle company-scoped, par exemple :
# src/catalogue/models/product.py

class Meta:
    default_manager_name = "objects"
```

Le comportement du `_base_manager` de Django devra être étudié et testé
séparément. Django recommande généralement de ne pas filtrer le base manager,
car il sert notamment à retrouver des objets liés.

Le nom `company` n'est pas retenu pour le manager mono-compagnie : il entrerait
en conflit avec le champ `company` présent sur ces modèles. Le nom conventionnel
`objects` exprime que le chemin normal est le chemin sécurisé.

---

## 7. `CompanyScopedManager` et absence de contexte

### Réflexion / options envisagées

Sans contexte, deux comportements sûrs ont été considérés :

- retourner `queryset.none()` ;
- lever une exception explicite.

Le queryset vide évite une fuite, mais peut masquer longtemps une erreur de
programmation dans une route globale. Une exception empêche également la fuite
et rend le défaut immédiatement visible dans les tests et les journaux.

### Décision finale

Sans scope mono-compagnie explicite, `CompanyScopedManager` lève une exception
dédiée. Il ne retourne jamais toutes les lignes.

```python
# Application : scope
# Fichier pressenti : src/scope/exceptions.py

class MissingCompanyScope(RuntimeError):
    pass
```

```python
# Application : scope
# Fichier pressenti : src/scope/managers.py

class CompanyScopedManager(models.Manager):
    def get_queryset(self):
        scope = get_request_scope()
        if scope.mode is not ScopeMode.COMPANY or scope.company_id is None:
            raise MissingCompanyScope(
                "A company-scoped queryset requires an active company scope."
            )

        return super().get_queryset().filter(company_id=scope.company_id)
```

Les trois situations suivantes sont complémentaires :

```text
/c/slug-inexistant/                  → middleware : 404
Product.objects sur une route globale → manager : exception de programmation
aucun contexte                        → jamais de queryset global implicite
```

---

## 8. Accès multi-compagnies explicite

### Réflexion / options envisagées

Un `MultiCompaniesScopedManager` aurait pu lire une liste depuis un contexte
ambiant. Cette liste n'est toutefois pas une propriété stable de l'URL `/mc/` :
elle dépend de l'utilisateur et de la fonctionnalité demandée.

Un manager non filtré avec `.filter(company_id__in=...)` dépendrait de la
discipline du développeur. Il serait possible d'oublier le filtre.

### Décision finale

Le manager `companies` force l'emploi de `for_companies()` :

```python
# Application : scope
# Fichier pressenti : src/scope/managers.py

class CompaniesScopedManager(models.Manager):
    def get_queryset(self):
        raise MissingCompaniesScope(
            "Use .for_companies(company_ids) explicitly."
        )

    def for_companies(self, company_ids):
        ids = tuple(company_ids)
        queryset = CompanyScopedQuerySet(self.model, using=self._db)
        if not ids:
            return queryset.none()
        return queryset.filter(company_id__in=ids)
```

Les appels suivants doivent échouer :

```python
Product.companies.all()
Product.companies.filter(name__icontains="shirt")
Product.companies.get(pk=1)
```

Le point d'entrée normal est :

```python
Product.companies.for_companies(authorized_company_ids)
```

Le code final devra vérifier les interactions avec les méthodes Django du
manager et du queryset afin qu'aucun raccourci ne contourne cette obligation.

---

## 9. Routes `/mc/` et employés autorisés

### Réflexion / options envisagées

Les vues multi-compagnies auraient pu être réservées au propriétaire. Le besoin
inclut toutefois des gestionnaires ayant accès à un dashboard consolidé sur une
ou plusieurs compagnies.

Une permission unique pourrait simultanément autoriser la fonctionnalité et
définir son périmètre. Cette approche confond deux questions :

1. l'utilisateur peut-il ouvrir le dashboard ?
2. quelles compagnies peuvent alimenter le dashboard ?

### Décision finale

`/mc/` est accessible au propriétaire et aux employés explicitement autorisés.

Une permission comme `reporting.dashboard.view`, de contexte
`MULTI_COMPANIES`, autorise la fonctionnalité. Le périmètre de données est
calculé séparément à partir des accès ordinaires de l'utilisateur.

```text
permission MULTI_COMPANIES valide
    → autorise l'utilisation du dashboard

périmètre des rôles/assignations valides
    → détermine les compagnies visibles
```

Flux cible :

```python
# Application : reporting
# Fichier pressenti : src/reporting/services/dashboard_service.py

authorized_ids = CompanyAccessService.authorized_company_ids(request.user)

requested_ids = parse_requested_company_ids(request)
final_ids = validate_requested_companies_strictly(
    requested_ids=requested_ids,
    authorized_ids=authorized_ids,
)

products = Product.companies.for_companies(final_ids)
```

La liste peut contenir zéro, une ou plusieurs compagnies. Le mode
multi-compagnies décrit la fonctionnalité et non un nombre minimal de deux
compagnies.

Les compagnies archivées sont exclues des rapports globaux selon la conception
actuelle, tout en restant consultables dans leurs vues `/c/<slug>/` par les
utilisateurs autorisés.

---

## 10. `CompanyAccessService`

### Réflexion / options envisagées

Le backend RBAC répond naturellement à une question booléenne :

```text
L'utilisateur possède-t-il cette permission dans ce contexte ?
```

Calculer toutes les compagnies accessibles est une opération différente. La
placer dans le middleware rendrait le middleware dépendant de chaque
fonctionnalité. La recalculer dans toutes les vues dupliquerait la logique.

### Décision finale

Un service dédié calcule le périmètre accessible :

```python
# Application : access
# Fichier pressenti : src/access/services/company_access_service.py

class CompanyAccessService:
    @classmethod
    def authorized_company_ids(cls, user):
        """Retourne les IDs de compagnies accessibles à l'utilisateur."""
        ...
```

Principes attendus :

- utilisateur inactif : aucun accès ;
- propriétaire actif : toutes les compagnies pertinentes pour la
  fonctionnalité ;
- employé : compagnies couvertes par ses rôles et assignations valides ;
- rôles, permissions et assignations inactifs : exclus ;
- règles `DELEGATE` : ne doivent pas accorder accidentellement des capacités
  opérationnelles ;
- le service retourne des identifiants ou un queryset maîtrisé, pas un manager
  global implicite.

Le service pourra accepter ultérieurement une permission ou un type d'accès si
le périmètre varie selon la fonctionnalité :

```python
CompanyAccessService.authorized_company_ids(
    user,
    permission="reporting.dashboard.view",
)
```

La signature exacte reste à définir après révision complète du RBAC.

---

## 11. Validation stricte des sélections multi-compagnies

### Réflexion / options envisagées

Si un utilisateur demande `[A, B]` mais n'est autorisé que pour `[A]`, deux
comportements sont possibles :

- intersection silencieuse et résultat limité à A ;
- refus complet de la demande.

L'intersection est conviviale pour des filtres périmés, mais peut faire croire
qu'un rapport A+B représente réellement les deux compagnies.

Le backend actuel utilise une condition `company_id__in` suivie de `exists()`.
Pour `[A, B]`, cette logique peut retourner vrai dès qu'une seule compagnie
correspond. Elle ne démontre pas l'accès à toutes les compagnies demandées.

### Décision finale

La validation est stricte :

```text
demandé   = [A, B]
autorisé  = [A]
résultat  = 403 Forbidden
```

Si aucune sélection n'est fournie, la fonctionnalité peut utiliser toutes les
compagnies autorisées et actives. Une liste autorisée vide produit un résultat
vide lorsque l'accès à la fonctionnalité elle-même demeure valide.

Exemple :

```python
# Application : access ou reporting
# Fichier pressenti :
# src/access/services/company_access_service.py

unauthorized_ids = set(requested_ids) - set(authorized_ids)
if unauthorized_ids:
    raise PermissionDenied("Unauthorized company selection.")
```

La branche `MULTI_COMPANIES` de `src/access/auth_backend.py` devra être corrigée
et couverte par des tests vérifiant l'accès à **toutes** les compagnies
demandées, et non à au moins une d'entre elles.

---

## 12. Manager technique non filtré

### Réflexion / options envisagées

L'administration Django, certaines migrations de données et les commandes de
maintenance ont parfois besoin de voir toutes les lignes. Le POC détecte ces
cas implicitement grâce à `sys.argv` et à l'inspection de la pile de l'admin.

Un accès technique entièrement supprimé compliquerait la maintenance. Un accès
automatique selon l'environnement est difficile à contrôler et à tester.

### Décision finale

L'accès non filtré est volontaire et explicite :

```python
Product.unscoped.all()
```

`UnscopedManager` apporte surtout :

- un nom et un type facilement repérables en revue de code ;
- une frontière explicite avec les accès métier ;
- un emplacement pour ajouter des garde-fous techniques ;
- la suppression des heuristiques liées à `sys.argv` et à la pile d'appel.

```python
# Application : scope
# Fichier pressenti : src/scope/managers.py

class UnscopedManager(models.Manager):
    """Accès technique non filtré; interdit dans les vues métier."""
```

L'admin demande explicitement ce queryset au lieu de rendre le manager
technique manager par défaut :

```python
# Application du modèle concerné
# Exemple pressenti : src/catalogue/admin.py
u
class ProductAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return Product.unscoped.all()
```

L'admin devra aussi limiter les choix de relations afin d'empêcher les liens
incohérents entre compagnies.

---

## 13. Modèles globaux, mixtes et managers adaptés

### Réflexion / options envisagées

Appliquer les trois managers à tous les modèles donnerait une apparence
d'uniformité, mais une fausse sécurité. Tous les modèles n'ont pas une colonne
`company_id` simple et obligatoire.

### Décision finale

Classification actuelle :

| Modèle/type                          | Classification                     | Orientation de manager                       |
| ------------------------------------ | ---------------------------------- | -------------------------------------------- |
| `Company`                            | global, pivot du scope             | manager Django normal                        |
| `User`                               | global                             | `CustomUserManager` habituel                 |
| `Permission`                         | référentiel global                 | manager normal                               |
| `Product`, `Location`, `Stock`, etc. | compagnie unique                   | trois managers scoped/multi/technique        |
| `Movement`                           | compagnie unique, immuable         | trois managers adaptés, écriture via service |
| `Role`                               | mixte, compagnie nullable          | queryset/service spécifique                  |
| `access.Log`                         | mixte, compagnie nullable          | queryset/service spécifique                  |
| `UserRoleLog`                        | journal global d'assignations      | manager normal, visibilité contrôlée         |
| `Image`                              | dépôt global, autorisation héritée | accès via l'objet propriétaire               |
| champs `AbstractAudit`               | héritent du modèle porteur         | aucune politique autonome                    |

Un modèle global n'est pas nécessairement visible par tout le monde. « Global »
signifie ici que son appartenance n'est pas déterminée par une seule compagnie.
Son accès demeure soumis au RBAC, à la hiérarchie des utilisateurs et aux
services métier.

---

## 14. Images et autorisation héritée

### Réflexion / options envisagées

Une image peut être liée à une compagnie, une location, un profil utilisateur,
une catégorie ou un produit. Il n'existe volontairement pas de permissions
génériques `core.image.view/add/change/delete` : les droits proviennent du
modèle fonctionnel auquel l'image est attachée.

Un simple endpoint récupérant une image par UUID pourrait contourner ce modèle
si l'objet propriétaire n'est pas retrouvé et autorisé.

### Décision finale

`Image` reste une ressource technique globale, mais :

- l'affichage passe par l'autorisation de l'objet propriétaire ;
- l'ajout, la modification et la suppression passent par le service du modèle
  propriétaire ;
- une image ne peut pas être réassignée d'un objet de A vers un objet de B sans
  validation explicite ;
- les fichiers privés ne doivent pas être servis uniquement parce que leur URL
  est connue ;
- aucun listing global d'images n'est exposé aux utilisateurs métier.

La structure exacte des relations d'images doit encore être révisée dans le
schéma de données.

---

## 15. Appartenance d'un objet à une compagnie

### Réflexion / options envisagées

Django autorise normalement :

```python
product.company_id = other_company.id
product.save()
```

Un manager filtrant les lectures n'empêche pas non plus toutes les écritures :

```python
Product.objects.create(company_id=other_company.id, ...)
Product.objects.filter(...).update(company_id=other_company.id)
Product.unscoped.bulk_update(...)
```

Contrôler seulement `save()` laisse ouverts `update()`, `bulk_update()`, les
relations inverses et certains chemins administratifs.

### Décision finale

Pour les modèles company-scoped, l'appartenance à la compagnie est immuable
après la création.

Une classe abstraite est envisagée pour centraliser une partie de la règle :

```python
# Application : scope ou core, à décider
# Fichier pressenti : src/scope/models.py

class CompanyOwnedModel(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    class Meta:
        abstract = True
```

Cette classe ne suffira pas à elle seule. Les méthodes suivantes devront être
contrôlées ou rendues inaccessibles par le chemin métier :

- `create`, `get_or_create`, `update_or_create` ;
- `update`, `bulk_create`, `bulk_update` ;
- `save` d'une instance existante ;
- relations inverses et formulaires admin ;
- imports et tâches de fond.

La compagnie d'une création mono-compagnie doit provenir du scope validé, et
non d'un identifiant libre fourni par le client.

---

## 16. Trois couches de protection des écritures

### Réflexion / options envisagées

Le manager est une excellente barrière contre les fuites en lecture, mais ne
peut garantir seul toutes les mutations. Le backend RBAC autorise une action,
mais n'exécute pas l'opération et ne valide pas tous ses invariants.

### Décision finale

Les écritures reposent sur trois couches applicatives complémentaires :

1. **Middleware/contexte** : installe le bon périmètre et peut refuser tôt une
   catégorie évidente de requêtes ;
2. **API ORM interne** : managers/querysets filtrants et appartenance immuable ;
3. **Services métier transactionnels** : permission, état, invariants, écritures
   liées et audit.

Le mot « API » désigne ici une interface Python interne, par exemple
`Product.objects` ou `ProductService.create_product()`. Il ne signifie pas une
API HTTP/JSON.

Exemple :

```python
# Application : catalogue
# Fichier pressenti : src/catalogue/services/product_service.py

class ProductService:
    @staticmethod
    @transaction.atomic
    def create_product(*, actor, company, data):
        if not actor.has_perm(
            "catalogue.product.add",
            obj={"company_id": company.id},
        ):
            raise PermissionDenied

        CompanyWritePolicy.ensure_writable(company)
        return Product.objects.create(**data)
```

`src/access/auth_backend.py` est un composant d'autorisation, pas un service
métier : il répond à `has_perm()`, mais ne crée pas un produit et ne pilote pas
une transaction complète.

---

## 17. Compagnies archivées et lecture seule

### Réflexion / options envisagées

Le champ a d'abord été pensé sous les noms `is_archived`, `is_active` ou
`is_read_only`. La règle métier précisée est plus forte qu'un simple affichage :
toutes les données appartenant à une compagnie inactive doivent être figées.

Bloquer uniquement les écritures dans `CompanyScopedQuerySet` ne couvre pas
`instance.save()`, les opérations bulk, l'admin, les tâches de fond ou les
modèles mixtes. Bloquer la compagnie inactive dans le middleware empêcherait
aussi sa consultation, pourtant requise.

### Décision finale

`Company.is_active=False` signifie :

- la compagnie demeure consultable par les utilisateurs autorisés ;
- son catalogue, son inventaire, sa configuration et ses données RBAC propres
  sont en lecture seule ;
- elle est exclue des rapports globaux/multi-compagnies selon la conception
  actuelle ;
- aucune insertion, mise à jour ou suppression de données lui appartenant
  n'est permise ;
- sa seule mutation permise est sa réactivation.

La vérification d'état est distincte du RBAC : même un propriétaire ne contourne
pas la lecture seule pour effectuer une autre écriture.

Les méthodes HTTP dites « non sûres » (`POST`, `PUT`, `PATCH`, `DELETE`) peuvent
être refusées tôt sur une route de compagnie inactive, mais cette barrière ne
remplace pas la politique d'écriture dans les services et l'ORM. Cette notion
est indépendante de HTTP contre HTTPS.

---

## 18. Réactivation d'une compagnie

### Réflexion / options envisagées

La réactivation aurait pu être une permission RBAC assignable. Elle aurait alors
été délégable à un employé. Cette opération modifie l'état fondamental de toutes
les données de la compagnie.

Une mise à jour générale de l'objet `Company` pourrait aussi permettre de
modifier plusieurs champs en prétendant effectuer une réactivation.

### Décision finale

La réactivation :

- est réservée à un utilisateur actif avec `is_owner=True` ;
- n'a pas de permission RBAC dédiée ;
- n'est jamais délégable ;
- autorise uniquement la transition `False → True` ;
- ne permet pas de modifier simultanément d'autres champs.

```python
# Application : company
# Fichier pressenti : src/company/services/company_lifecycle_service.py

class CompanyLifecycleService:
    @staticmethod
    @transaction.atomic
    def reactivate(*, actor, company):
        if not actor.is_active or not actor.is_owner:
            raise PermissionDenied
        if company.is_active:
            return company

        # Mise à jour ciblée du seul champ autorisé.
        ...
```

L'archivage est également une action owner-only selon la conception actuelle.

---

## 19. Transit inter-compagnies

### Réflexion / options envisagées

`inventory.Transit` possède actuellement des informations source et
destination. Il ne correspond donc pas au modèle simple « une ligne appartient
à la compagnie source ».

Après expédition par A vers B, les informations source sont figées. Le transit
disparaît entièrement du périmètre de A et devient un document de suivi destiné
à B. B peut renseigner ses champs de réception même si A est archivée.

Les clés étrangères source pourraient exposer ou coupler inutilement les
données internes de A. Un snapshot JSON a été envisagé pour préserver seulement
les informations pertinentes à la réception.

### Décision finale

Orientation métier retenue pour la future V1 :

```text
création par A
→ bloc source figé
→ remise au périmètre de B
→ bloc destination modifiable par B
→ complétion
```

Le transit appartient fonctionnellement à la compagnie destinataire après
l'expédition. Les champs source ne sont ni modifiables ni visibles par B au-delà
des informations nécessaires au suivi.

`company_dest_id` devrait probablement rester une FK structurante pour le
cloisonnement et l'intégrité. Les informations métier source pertinentes
pourraient devenir un snapshot immuable. La table sera révisée avant son
développement final ; elle ne doit pas être forcée dans le manager générique
avant que sa propriété exacte soit modélisée.

---

## 20. Tâches de fond et commandes

### Réflexion / options envisagées

Les tâches asynchrones, imports CSV et commandes ne passent pas par le
middleware HTTP. Leur accorder automatiquement un accès global parce que
`manage.py` figure dans `sys.argv` rend leur comportement implicite.

### Décision finale

Une tâche de fond choisit explicitement son périmètre :

```python
# Application : scope
# Fichier pressenti : src/scope/context.py

with company_scope(company_id):
    Product.objects.all()
```

ou :

```python
Product.companies.for_companies(company_ids)
```

Une opération de maintenance réellement globale utilise consciemment :

```python
Product.unscoped.all()
```

Le context manager devra utiliser les tokens de `contextvars` afin de restaurer
le contexte précédent même lorsqu'une exception survient.

---

## 21. Django avec templates ou frontend séparé

### Réflexion / options envisagées

Une séparation complète en backend Django Ninja/DRF et frontend distinct a été
envisagée pour enrichir le portfolio. Elle ajouterait toutefois immédiatement :

- authentification interapplications ;
- CORS et CSRF ;
- sérialisation ;
- deux déploiements ;
- gestion d'erreurs réseau ;
- davantage de tests et de plomberie.

Elle ne résout pas le cloisonnement : une API HTTP peut fuir des données entre
compagnies exactement comme une vue Django avec templates.

### Décision finale

La V1 reste une application Django avec templates. Les vues doivent utiliser
des services métier suffisamment séparés pour qu'une API Django Ninja puisse
être ajoutée ultérieurement sans réécrire la logique de sécurité.

---

## 22. HTTPS et méthodes HTTP

### Réflexion / options envisagées

L'expression « méthode HTTP non sûre » a été initialement comprise comme une
obligation HTTPS. Elle désigne plutôt les méthodes ayant normalement un effet
sur l'état : `POST`, `PUT`, `PATCH` et `DELETE`.

### Décision finale

Le développement local peut continuer en HTTP. HTTPS sera configuré au moment
d'un éventuel déploiement ; des certificats gratuits ou locaux sont possibles
et ne nécessitent pas de modifier l'architecture des scopes.

Les requêtes `GET`, `HEAD` et `OPTIONS` ne doivent pas produire de mutation.
Les méthodes d'écriture sur une compagnie inactive peuvent être rejetées tôt,
en complément des protections ORM et métier.

---

## 23. Tests de sécurité indispensables

### Réflexion / options envisagées

Les managers et le contexte réduisent les risques d'erreur, mais leur valeur
dépend de tests prouvant que chaque chemin se ferme correctement. Les tests ne
doivent pas bénéficier automatiquement d'un manager global parce qu'ils sont
exécutés par `pytest`.

### Décision finale

La suite devra couvrir au minimum :

### Mono-compagnie

- `/c/inconnue/...` retourne `404` ;
- compagnie existante mais inaccessible retourne `403` ;
- owner sur `/c/A/...` ne voit jamais B ;
- `Product.objects` sans contexte lève `MissingCompanyScope` ;
- le contexte est nettoyé après succès et après exception ;
- deux requêtes concurrentes ne partagent jamais leur contexte.

### Multi-compagnies

- `Product.companies.all()` et `.filter()` sont refusés ;
- `for_companies([])` retourne un queryset vide ;
- un employé autorisé au dashboard ne voit que son périmètre ;
- demander au moins une compagnie interdite produit `403` ;
- l'accès à A ne suffit pas à valider `[A, B]` ;
- les compagnies archivées sont exclues des consolidations.

### Écritures

- création dans une compagnie différente du scope refusée ;
- changement de `company_id` après création refusé ;
- `update`, `bulk_create` et `bulk_update` ne contournent pas la règle ;
- compagnie inactive entièrement en lecture seule ;
- owner soumis à la lecture seule comme les employés ;
- réactivation owner-only et limitée au champ `is_active`.

### Administration et infrastructure

- l'admin emploie explicitement `unscoped` ;
- les choix de FK admin ne permettent pas de relation inter-compagnies invalide ;
- les tâches de fond ouvrent explicitement un scope ;
- aucun comportement global ne dépend de `sys.argv`, `pytest` ou de la pile.

### Modèles particuliers

- visibilité des logs conforme à leur périmètre ;
- une image ne contourne pas l'autorisation de son propriétaire ;
- un mouvement est company-scoped et immuable ;
- les données source d'un transit terminé ne redeviennent pas accessibles à A.

---

## 24. Points encore ouverts

### Réflexion / options envisagées

L'atelier a arrêté les frontières principales, mais certaines décisions exigent
la révision du schéma et des prototypes avant de choisir une implémentation
précise.

### Décision finale / travaux à poursuivre

Les points suivants ne sont **pas encore définitivement arrêtés** :

1. structure exacte de `RequestScope` et nomenclature finale du middleware ;
2. migration de la regex actuelle vers `process_view()` ;
3. critère minimal permettant à un utilisateur d'entrer dans une compagnie ;
4. algorithme exact de `CompanyAccessService.authorized_company_ids()` ;
5. interaction précise entre permission `MULTI_COMPANIES` et assignations de
   rôles company-scoped :
   - La permission MULTI_COMPANIES autorise la fonctionnalité.
   - Les assignations COMPANY/LOCATION actives déterminent le périmètre.
   - La permission MULTI_COMPANIES n’élargit jamais ce périmètre.
6. configuration de `_base_manager` pour les relations Django ;
7. garde-fous exacts de `UnscopedManager` ;
8. moyen de protéger tous les chemins bulk sans rendre l'ORM inutilisable ;
9. modèle de propriété et de diffusion des images ;
10. structure finale de `inventory.Transit` ;
11. modélisation et filtrage de `Role` et `access.Log`, dont `company_id` est
    nullable ;
12. stratégie de service et de validation entourant l'admin Django.

Ces questions doivent être résolues avant de présenter les exemples de ce
document comme une implémentation finale.

---

## 25. Architecture cible résumée

### Réflexion / options envisagées

Le risque principal est qu'un filtre oublié retourne les données d'une autre
compagnie. La solution ne doit toutefois pas transformer le middleware ou le
manager en composant omniscient.

### Décision finale

```text
/c/<company_slug>/...
    → middleware résout la compagnie ou retourne 404
    → contexte mono-compagnie explicite
    → vérification d'accès / permission : 403 au besoin
    → Model.objects filtre automatiquement
    → service métier contrôle les écritures

/mc/...
    → permission MULTI_COMPANIES pour la fonctionnalité
    → CompanyAccessService calcule le périmètre
    → sélection demandée validée strictement
    → Model.companies.for_companies(ids)

/g/...
    → aucun scope mono-compagnie implicite
    → modèles globaux et règles SYSTEM/owner

/admin/... et maintenance
    → unscoped explicite
    → contrôles renforcés des relations et mutations
```

Principes directeurs :

- fermeture par défaut ;
- périmètre mono-compagnie explicite dans l'URL ;
- périmètre multi-compagnies explicite dans le code ;
- aucun bypass implicite selon le processus ou la pile d'appel ;
- owner ne signifie pas queryset global dans `/c/` ;
- autorisation RBAC distincte de l'état métier ;
- appartenance à une compagnie immuable ;
- compagnies archivées consultables mais non modifiables ;
- services métier transactionnels pour les mutations ;
- tests d'isolation comme composante essentielle de l'architecture.
