<div align="center">

<img src="../assets/img/logo.svg" alt="Logo Gestion de stocks" width="60" />

# Sécurité des données

Projet Gestion de stocks — document de travail

<img src="https://img.shields.io/badge/Statut_du_document-V1_Prêt_pour_POC-purple.svg" alt="Statut" />

</div>

Ce document documente le système de contrôle d'accès basé sur les rôles (**RBAC - Role-Based Access Control**) qui sera utilisé par l'application de Gestion de Stocks. L'architecture est conçue pour être granulaire, isolée par entreprise, et évolutive. Cette architecture s'appuie sur le système d'authentification natif de Django et l'étend.

---

## 1. Principes et analyse des besoins

Django met en oeuvre nativement un contrôle d'accès basé sur les rôles (RBAC) où les concept de **Permissions** et de **Rôles** sont utilisés comme fondations :

* **Permissions** : Une action précise que l'utilisateur a le droit d'effectuer (ex: *Créer un produit*, *Voir une page*).
  * Django génère automatiquement les 4 permissions CRUD pour chaque modèle (`view`, `add`, `change`, `delete`).
* **Rôles (Groupes)** : Un ensemble de permissions rassemblés sous un même identifiant (ex: *Gestionnaire*, *Magasinier*, *Vendeur*).
  * Django utilise le terme *Group* pour désigner les rôles. Django crée les structures de DB nécessaires mais ne génère aucun rôle par défaut.
* **Assignations** : Les utilisateurs sont assignés aux rôles, ce qui donne automatiquement toutes les permissions associées.
  * Django gère cette relation via une table intermédiaire lié au modèle utilisateur `AUTH_USER_MODEL`. Ces assignations sont *globales à toute la base de données*. Ainsi, un utilisateur ayant le droit de modifier un produit peut modifier n'importe quel produit sans restriction.
* **Concept de super-utilisateur (`is_superuser`)** : Un super-utilisateur possède toutes les permissions existantes et futures indépendamment des rôles et permissions qui lui sont explicitement assignés.
* **Concept d'utilisateur inactif (`is_active`)** : Un utilisateur inactif (`is_active=False`) n'a aucun accès, peu importe les rôles et permissions qui lui sont assignés.

En plus du comportement CRUD standard, cette application de gestion de stocks multi-entreprises impose des contraintes de sécurité spécifiques :

* **Isolation par Entreprise (`Company`):** Un utilisateur possède des permissions distinctes pour chaque entreprise.
  * *Exemple* : un utilisateur peut être *Gestionnaire* et *Vendeur* dans l'Entreprise A et disposer uniquement d'un rôle en *Lecture seule* dans l'Entreprise B.
* **Permissions granulaires**: Certaines permissions ne s'alignent pas sur le modèle CRUD global.
  * *Exemple 1 (Métier)* : Un vendeur a le droit de diminuer l'inventaire lors d'une vente (`movement.sale`), mais n'a pas le droit de déclarer une perte par bris (`movement.loss`), ni d'augmenter le stock. Le droit est lié au contexte du mouvement et non au simple droit de modification (`change_stock`) du modèle.
  * *Exemple 2 (Interface)* : un gestionnaire a accès aux graphiques d'alerte de seuil bas (`dashboard.view_stock_levels`), mais pas aux graphiques financiers (permission granulaire sur des vues qui rassemblent les données de plusieurs modèles).

### 1.1. Limitations dans les contrôles d'accès natif de Django

Les permissions natives CRUD de Django lient l'utilisateur et le modèle globalement. Ainsi, le systeme natif de Django ne peut pas, tel quel, répondre aux besoins concernant l'**Isolation par Entreprise** ou les **Permissions granulaires**.

## 2. Extension du système de permissions de Django

Pour répondre aux exigences d'**Isolation par Entreprise** et de **Permissions granulaires**, le système natif de Django est étendu à travers deux mécanismes complémentaires :

* un modèle d'affectation tripartite basé sur le scope géographique
* des métadonnées de modèles personnalisées.

### Modèle d'affection tripartite pour répondre à l'exigence d'isolation par Entreprise

L'application contourne le système d'affectation global de Django en introduisant un modèle intermédiaire personnalisé. Ce modèle lie un utilisateur (`User`), un rôle d'autorisation Django standard (`Group`) et une entreprise (`Company`), tout en offrant la possibilité de restreindre ce rôle à un emplacement physique spécifique (`Location`).


| user_role (Table de liaison) |
| :--------------------------- |
| id PK                        |
| user_id FK                   |
| company_id FK                |
| role_id FK                   |
| location_id FK, NULLABLE     |

```python
# Dans users/models.py
# ...
from django.utils.translation import gettext_lazy as _
class Role(models.Model):
   user = models.ForeignKey(
      settings.AUTH_USER_MODEL, 
      on_delete=models.CASCADE, 
      related_name='access'
   )
   company = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
   role = models.ForeignKey(Group, on_delete=models.CASCADE)
   location = models.ForeignKey(
      'companies.Location', 
      on_delete=models.CASCADE, 
      null=True, 
      blank=True,
      related_name='localized_roles'
   )

   class Meta:
      unique_together = ('user', 'company', 'role', 'location')
      verbose_name = _("Company Access")
      verbose_name_plural = _("Company Accesses")
```

Pour exploiter cette structure, le modèle d'utilisateur personnalisé expose une méthode centralisée de vérification des droits, capable d'évaluer les permissions globales (entreprise) et locales (boutique/entrepôt) :

```python
# Dans users/models.py
class User(AbstractUser):
    # Champs personnalisés...

    def has_location_perm(self, company_id, permission_codename, location_id=None):
        """Vérifie si l'utilisateur a une permission spécifique dans une entreprise donnée.
        Prend en charge la restriction optionnelle par location."""
        if self.is_superuser:
            return True

       if not self.is_active:
        return False

       # Si le codename arrive sous la forme complète (ex: 'catalogue.add_product'), 
       # on extrait uniquement le codename strict requis par la table auth_permission
       if "." in permission_codename:
         permission_codename = permission_codename.split(".")[-1]

      # L'utilisateur a le droit si :
      # 1. Il a le rôle au niveau global de la Company (location_id IS NULL)
      # 2. OU il a le rôle spécifiquement pour la Location de l'action
      return self.access.filter(
          company_id=company_id,
          role__permissions__codename=permission_codename
      ).filter(
          models.Q(location__isnull=True) | models.Q(location_id=location_id)
      ).exists()

```

#### Application dans les Vues Django :

```python
# Exemple 1 : Action globale (Ajout d'un produit au catalogue de l'entreprise)
if not request.user.has_location_perm(current_company_id, 'catalogue.add_product'):
    raise PermissionDenied()

# Exemple 2 : Action localisée (Enregistrement d'une perte dans la Boutique B)
if not request.user.has_location_perm(current_company_id, 'inventory.loss', location_id=target_location_id):
    raise PermissionDenied()
```

> [!CAUTION]
> **Règle absolue de développement** : Ne jamais exécuter de requêtes larges de type `Product.objects.all()` a moins d'être dans un contexte de super_user. Toutes les requêtes d'extraction de données doivent être systématiquement filtrées par le contexte de l'entreprise active (ex: `Product.objects.filter(company_id=current_company_id)`).

### Permissions granulaires

Créer des permissions personnalisées (Custom Permissions), déclarer dans la classe Meta des modèles. Voici un exemple type pour la gestion de la modification des quantités en inventaire.

```python
# Dans inventory/models.py
class Movement(models.Model):
   # Champs existants...
   company = models.ForeignKey('entreprises.Entreprise', on_delete=models.CASCADE)
   quantite = models.IntegerField()
   # ...

   class Meta:
      permissions = [
         ("purchase", "Enregistrer des entrées depuis un fournisseur externe (achat)"),
         ("manufacture", "Enregistrer des entrées issues d'une production interne (fabrication)"),
         ("transfer_in", "Réceptionner du stock provenant d'un transfert interne (entrée)"),
         ("sale", "Enregistrer des sorties pour livraison client (vente)"),
         ("loss", "Sortir du stock défectueux, périmé ou perdu (perte)"),
         ("transfer_out", "Expédier du stock vers un transfert interne (sortie)"),
         ("relocate", "Déplacer du stock entre des sous-locations (étagères/zones)"),
      ]
```

> [!TIP]
> **Contrôle de l'Interface Utilisateur (UI)** : Lors de la génération des formulaires de mouvements de stock, les options disponibles dans le menu déroulant du champ `reason` (Raison du mouvement) doivent être filtrées dynamiquement dans le code Python en fonction des permissions effectives de l'utilisateur connecté, empêchant toute soumission frauduleuse.

## 3. Référentiel des permissions

Les permissions sont pré-définies dans le code de l'application et classées par applications.

> [!TIP]
> *Les fonctionnalités sous-jacentes à chaque permission seront implémentées à différents stades du développement (V1 à VX), certaines étant listées à des fins de planification de l'architecture.*

### 🛠️ 3.1. Application Core (`core.*`)

Centralise les configurations globales et les paramètres techniques du système.


| Code de permission    | Type        | Description                                                           |
| :-------------------- | :---------- | :-------------------------------------------------------------------- |
| `core.view_setting`   | Django CRUD | Consulter les configurations globales (devises, modes d'accès).      |
| `core.change_setting` | Django CRUD | Modifier les paramètres système généraux (Super-User uniquement). |

### 👥 3.2. Application Users (`users.*`)

Gère les profils utilisateurs et l'attribution des accès au sein des organisations.


| Code de permission   | Type           | Description                                                                      |
| :------------------- | :------------- | :------------------------------------------------------------------------------- |
| `users.view_user`    | Django CRUD    | Consulter la liste et les fiches des utilisateurs.                               |
| `users.add_user`     | Django CRUD    | Inviter ou créer un nouvel utilisateur dans le système.                        |
| `users.change_user`  | Django CRUD    | Modifier les informations d'un utilisateur existant.                             |
| `users.delete_user`  | Django CRUD    | Révoquer ou désactiver le compte d'un utilisateur.                             |
| `users.manage_roles` | Personnalisée | Créer, modifier ou attribuer les rôles et permissions au sein de l'entreprise. |

### 🏢 3.3. Application Companies (`companies.*`)

Pilote les entités juridiques (compagnies) et cartographie l'infrastructure physique (emplacements et sous-locations).


| Code de permission               | Type           | Description                                                              |
| :------------------------------- | :------------- | :----------------------------------------------------------------------- |
| `companies.view_company`         | Django CRUD    | Voir les informations de l'entreprise.                                   |
| `companies.add_company`          | Django CRUD    | Créer une nouvelle entreprise dans le système (Super-User uniquement). |
| `companies.change_company`       | Django CRUD    | Modifier les informations légales de l'entreprise.                      |
| `companies.view_location`        | Django CRUD    | Consulter la cartographie des sites, dépôts et boutiques.              |
| `companies.add_location`         | Django CRUD    | Créer un emplacement de haut niveau (Dépôt/Boutique).                 |
| `companies.change_location`      | Django CRUD    | Modifier la structure ou l'adresse d'un emplacement.                     |
| `companies.delete_location`      | Django CRUD    | Supprimer un emplacement (si aucun stock n'y est rattaché).             |
| `companies.manage_sub_locations` | Personnalisée | Créer ou modifier l'agencement fin interne (zones, étagères, frigos). |

### 🗂️ 3.4. Application Catalogue (`catalogue.*`)

Structure le référentiel des articles disponibles à la gestion de stock.


| Code de permission          | Type           | Description                                                           |
| :-------------------------- | :------------- | :-------------------------------------------------------------------- |
| `catalogue.view_product`    | Django CRUD    | Consulter le catalogue des fiches produits.                           |
| `catalogue.add_product`     | Django CRUD    | Créer une nouvelle référence d'article dans le catalogue.          |
| `catalogue.change_product`  | Django CRUD    | Modifier les caractéristiques d'une fiche produit.                   |
| `catalogue.delete_product`  | Django CRUD    | Supprimer définitivement un produit du catalogue de l'entreprise.    |
| `catalogue.view_category`   | Django CRUD    | Consulter l'arborescence des catégories de classement.               |
| `catalogue.add_category`    | Django CRUD    | Créer une catégorie ou sous-catégorie d'articles.                  |
| `catalogue.change_category` | Django CRUD    | Modifier ou réorganiser la hiérarchie des catégories.              |
| `catalogue.import_export`   | Personnalisée | Exécuter des imports ou exports massifs de données catalogue (CSV). |

### 📦 3.5. Application Inventory (`inventory.*`)

Gère l'état des stocks réels et encadre rigoureusement l'historique des flux logistiques.


| Code de permission                           | Type           | Description                                                                          |
| :------------------------------------------- | :------------- | :----------------------------------------------------------------------------------- |
| `inventory.view_stock`                       | Django CRUD    | Consulter les niveaux de stock disponibles par emplacement.                          |
| `inventory.view_movement`                    | Django CRUD    | Consulter le journal historique des mouvements de stock.                             |
| **Permissions de Mouvements Spécifiques :** |                | *(Déclenchent une écriture comptable dans le journal)*                             |
| `inventory.movement_purchase`                | Personnalisée | Enregistrer des entrées de stock depuis un fournisseur (Achat).                     |
| `inventory.movement_manufacture`             | Personnalisée | Enregistrer des entrées issues d'une chaîne de production interne.                 |
| `inventory.movement_sale`                    | Personnalisée | Enregistrer des sorties de stock pour livraison (Vente).                             |
| `inventory.movement_loss`                    | Personnalisée | Sortir des marchandises pour motif de casse, vol ou péremption (Perte).             |
| `inventory.movement_transfer_in`             | Personnalisée | Réceptionner et valider du stock provenant d'un transfert inter-location (Transit). |
| `inventory.movement_transfer_out`            | Personnalisée | Expédier et diminuer le stock pour un transfert inter-site (Transit).               |
| `inventory.movement_relocate`                | Personnalisée | Réassigner un produit d'une sous-location à une autre (ex: Étagère A à B).      |

### 📊 3.6. Application Reporting (`reporting.*`)

Pilote l'accès aux indicateurs de performance, d'audit et d'analyse financière.


| Code de permission            | Type           | Description                                                                  |
| :---------------------------- | :------------- | :--------------------------------------------------------------------------- |
| `reporting.view_stock_levels` | Personnalisée | Accéder aux rapports de rotations, ruptures imminentes et seuils d'alerte.  |
| `reporting.view_financials`   | Personnalisée | Consulter la valorisation comptable des stocks et les graphiques financiers. |

## 4. Rôles par Défaut

Lorsqu'une nouvelle entreprise (`Company`) est initialisée dans le système, l'application génère automatiquement 4 rôles (Groupes Django) prédéfinis pour cette organisation. Le propriétaire de l'entreprise peut ensuite personnaliser la liste des permissions de ces rôles ou en créer de nouveaux depuis son espace d'administration.

### A. Propriétaire (`Owner`)

Possède l'intégralité des permissions disponibles dans l'application pour son organisation. C'est le seul rôle à détenir initialement le droit de gestion administrative des accès.

* **Permissions affectées** : Toutes les permissions des scopes `users.*`, `companies.*`, `catalogue.*`, `inventory.*` et `reporting.*`.
* **Périmètre par défaut** : Global (Entreprise complète).

### B. Gestionnaire d'Entrepôt / Magasinier en Chef

Responsable de l'approvisionnement, de la justesse des inventaires physiques et de la configuration du catalogue d'articles locaux.

* **Permissions affectées** :
  * `companies.view_company`, `companies.view_location`, `companies.manage_sub_locations`
  * `catalogue.view_product`, `catalogue.add_product`, `catalogue.change_product`, `catalogue.view_category`
  * `inventory.view_stock`, `inventory.view_movement`
  * `inventory.movement_purchase`, `inventory.movement_manufacture`, `inventory.movement_loss`, `inventory.movement_transfer_in`, `inventory.movement_transfer_out`, `inventory.movement_relocate`
  * `reporting.view_stock_levels`
* **Périmètre recommandé** : Global (ou restreint à un grand entrepôt de stockage).

### C. Opérateur / Employé de Magasin

Profil terrain dédié aux tâches logistiques quotidiennes : réception, rangement et expédition. Il ne peut pas modifier les fiches produits ni déclarer des pertes sèches sans validation.

* **Permissions affectées** :
  * `companies.view_location`
  * `catalogue.view_product`
  * `inventory.view_stock`, `inventory.view_movement`
  * `inventory.movement_transfer_in`, `inventory.movement_relocate`
* **Périmètre recommandé** : Restreint à l'emplacement physique d'affectation (ex: Boutique B uniquement).

### D. Auditeur / Comptable (Lecture Seule)

Profil de consultation destiné au suivi de la santé financière, à la valorisation des stocks et aux inventaires comptables de fin d'année.

* **Permissions affectées** :
  * `companies.view_company`, `companies.view_location`
  * `catalogue.view_product`, `catalogue.view_category`
  * `inventory.view_stock`, `inventory.view_movement`
  * `reporting.view_stock_levels`, `reporting.view_financials`
* **Périmètre recommandé** : Global (Entreprise complète).


### <a id="isolation_rôles">4.1. Choix architectural : Isolation des Rôles (Groupes Django)

Django ne permet pas de définir un AbstractGroup personnalisé comme il le fait pour le AbstractUser. AInsi, pour permettre à chaque entreprise de personnaliser les permissions de ses rôles sans affecter les autres entreprise, l'application utilise la nomenclature technique suivante en arrière-plan sur le champ `Group.name` : `{company_id}_{nom_du_role}` À l'affichage (Interface Utilisateur et Administration), le préfixe numérique est masqué via un traitement de chaîne (`name.split('_')[-1]`) pour offrir une expérience utilisateur naturelle et standardisée.**. Il est aussi envisager de permettre des rôles globaux pour toutes les compagnies à la fois en utilisant le préfixe "0_".
