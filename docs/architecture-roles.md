# 🔐 Architecture de Sécurité : RBAC Multi-Entreprises

Ce document spécifie le système de contrôle d'accès basé sur les rôles (**RBAC - Role-Based Access Control**) pour le projet *Gestion de Stocks*. L'architecture est conçue pour être granulaire, isolée par entreprise, et évolutive.

---

## 🎯 1. Principes Fondamentaux

Pour concilier la simplicité de gestion et la finesse des droits, l'architecture sépare les concepts d'**Atomes** et de **Blocs** :

* **Atome (Permission) :** Une action technique ou visuelle indivisible et immuable dans le code (ex: *créer une vente*, *voir le graphique financier*).
* **Bloc (Rôle) :** Un ensemble nommé de plusieurs atomes (ex: *Gestionnaire d'entrepôt*). Les rôles sont assignés aux utilisateurs et sont entièrement configurables par les propriétaires d'entreprises.
* **Isolation par Entreprise :** Un utilisateur possède un profil et des rôles distincts pour chaque entreprise (`Company`). Il peut être *Propriétaire* chez l'Entreprise A et simple *Lecture seule* chez l'Entreprise B.

---

## ⚛️ 2. Référentiel des Atomes (Permissions)

Les permissions sont pré-définies dans le code de l'application et classées par domaine.

### 📦 Mouvements de Stock (`movement.*`)

La gestion des flux repose entièrement sur la granularité des types de mouvements de l'entité `Movement`.


| Sens        | Type de Mouvement | Code de l'Atome         | Description                                                    |
| :---------- | :---------------- | :---------------------- | :------------------------------------------------------------- |
| **ENTRÉE** | Achat             | `movement.purchase`     | Enregistrer des entrées depuis un fournisseur externe         |
| **ENTRÉE** | Fabrication       | `movement.manufacture`  | Enregistrer des entrées issues d'une production interne       |
| **ENTRÉE** | Transfert entrant | `movement.transfer_in`  | Réceptionner du stock provenant d'un autre site               |
| **SORTIE**  | Vente             | `movement.sale`         | Enregistrer des sorties pour livraison client                  |
| **SORTIE**  | Perte / Bris      | `movement.loss`         | Sortir du stock défectueux, périmé ou perdu                 |
| **SORTIE**  | Transfert sortant | `movement.transfer_out` | Expédier du stock vers un autre site de l'entreprise          |
| **INTERNE** | Réassignation    | `movement.relocate`     | Déplacer ou réorganiser des produits au sein d'un même site |

### 🗂️ Catalogue & Infrastructure (`catalogue.*` / `infra.*`)

* `catalogue.view` : Consulter le catalogue des produits et catégories.
* `catalogue.create_edit` : Ajouter ou modifier une fiche produit / catégorie.
* `catalogue.delete` : Supprimer un produit du catalogue.
* `catalogue.import_export` : Importer ou exporter le catalogue au format CSV.
* `infra.manage_locations` : Créer, modifier ou supprimer des sites (dépôts, boutiques).

### 📊 Tableaux de Bord & Reporting (`dashboard.*`)

* `dashboard.view_stock_levels` : Voir les alertes de seuils critiques et volumes globaux.
* `dashboard.view_financials` : Voir les graphiques de valeurs de stocks et de ventes mensuelles.

### ⚙️ Administration de l'Entreprise (`company.*`)

* `company.manage_members` : Inviter des utilisateurs et modifier leurs rôles.
* `company.manage_roles` : Créer ou personnaliser les blocs de rôles de l'entreprise.

---

## 👥 3. Rôles par Défaut (Semés à la création)

Lorsqu'une nouvelle `Company` est créée, le système génère automatiquement 4 rôles par défaut. Le propriétaire peut ensuite modifier la liste des atomes de ces rôles ou en créer de nouveaux.

1. **Propriétaire (`Owner`) :** Possède l'intégralité des atomes disponibles. C'est le seul rôle ayant initialement le droit `company.manage_roles`.
2. **Gestionnaire d'Entrepôt :**
   * *Mouvements :* `purchase`, `manufacture`, `transfer_in`, `transfer_out`, `relocate`, `loss`
   * *Catalogue & Infra :* `catalogue.view`, `catalogue.create_edit`, `infra.manage_locations`
   * *Dashboard :* `dashboard.view_stock_levels`
3. **Opérateur / Employé :**
   * *Mouvements :* `transfer_in`, `relocate`
   * *Catalogue & Infra :* `catalogue.view`
4. **Lecture Seule (Auditeur/Comptable) :**
   * *Catalogue & Infra :* `catalogue.view`
   * *Dashboard :* `dashboard.view_stock_levels`, `dashboard.view_financials`

---

## 📐 4. Schéma des Modèles de Données Django

Pour supporter cette logique sans dépendre du système de groupes globaux de Django, les modèles suivants seront implémentés dans l'application `users` ou `main`.

```text
+---------------+         +-----------------------+         +-----------------+
|     User      |         |      Membership       |         |     Company     |
+---------------+         +-----------------------+         +-----------------+
| id            | 1     * | id                    | *     1 | id              |
| username      |-------->| user_id (FK)          |<--------| name            |
| ...           |         | company_id (FK)       |         | ...             |
+---------------+         +-----------------------+         +-----------------+
                                      | *
                                      |
                                      | * (M2M)
                          +-----------------------+
                          |         Role          |
                          +-----------------------+
                          | id                    |
                          | company_id (FK)       |
                          | name                  |
                          | permissions (JSON)    | --> Ex: ["movement.purchase", ...]
                          +-----------------------+
```

### Spécifications des champs :

* **`Role.permissions` :** Stocké sous forme de liste de chaînes de caractères au format `JSONField` pour conserver une structure plate, rapide à lire et facilement éditable.
* **`Membership` :** Table de liaison explicite (pivot) matérialisant l'affectation d'un utilisateur à un périmètre d'entreprise avec un ou plusieurs rôles.

---

## 🛠️ 5. Implémentation Technique & Helper

Un helper d'autorisation sera exposé sur le modèle `User` personnalisé pour valider les accès dans les vues et les templates Django :

```python
# Signature théorique du helper
def has_company_perm(self, company, permission_code: str) -> bool:
    """
    1. Récupérer le Membership de l'user pour cette company.
    2. Extraire tous les rôles associés.
    3. Fusionner les listes d'atomes (permissions JSON).
    4. Vérifier si permission_code est présent dans l'union des atomes.
    """
```

### Usage dans une vue Django :

```python
if not request.user.has_company_perm(current_company, 'movement.purchase'):
    raise PermissionDenied()
```

---

## 🛡️ 6. Évolution Future : Délégation de Pouvoir (Prévention de l'escalade)

L'architecture sécurise nativement le futur jalon de délégation de gestion (ex: un Directeur assignant des droits à un employé).

Lorsqu'un utilisateur $X$ tente d'affecter un rôle $R$ contenant un ensemble de permissions $P_R$ à un collaborateur au sein d'une entreprise $C$, le système appliquera la règle stricte de sous-ensemble suivante avant de valider la transaction :

$$
P_R \subseteq \text{Permissions effectives de } X \text{ dans } C
$$

**Règle :** Un utilisateur ne peut ni attribuer, ni retirer, ni créer un rôle contenant une permission qu'il ne possède pas lui-même dans cette entreprise.
