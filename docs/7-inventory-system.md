<div align="center">%

<img src="../assets/img/logo.svg" alt="Logo Gestion de stocks" width="60" />

# Opérations et invariants du système d’inventaire

Projet Gestion de stocks — document de conception

![Statut](https://img.shields.io/badge/Statut_du_document-En_cours_de_rédaction-purple.svg)

</div>

Ce document décrit les opérations autorisées sur les stocks, leurs préconditions et les invariants qui doivent être maintenus.

[← Base de données](6-database-models.md) | [Sommaire](2-conception.md) |  [Arborescence du projet →](8-project-structure.md)


## 1. Objectif

Ce document décrit les opérations autorisées sur les stocks, leurs préconditions et les invariants qui doivent être maintenus.

Une opération métier peut modifier plusieurs lignes de `inventory_stock`, mais toutes ses écritures doivent appartenir à une seule transaction atomique.

Le modèle `inventory_movement` constitue un journal historique immuable. Un mouvement enregistré ne peut jamais être modifié ou supprimé, même par un propriétaire. Une erreur historique doit être corrigée par une nouvelle opération compensatoire.

## 2. Terminologie

### Quantité conditionnée (packaging)

La quantité conditionnée représente le nombre d’exemplaires physiques d’un conditionnement donné.

Exemple :

```text
pack_quantity = 6
packaging = caissette de 30 œufs
```

### Quantité de référence

La quantité de référence est calculée à partir du conditionnement :

```text
ref_quantity = pack_quantity × packaging.ratio
```

Exemple :

```text
6 caissettes × 30 œufs = 180 œufs
```

### Opération métier

Une opération métier représente l’intention complète de l’utilisateur : réceptionner, vendre, déplacer ou reconditionner du stock.

Une opération peut produire une ou plusieurs modifications de stock et une ou plusieurs entrées dans le journal des mouvements.

### Mouvement compensatoire

Un mouvement compensatoire corrige les effets d’un mouvement antérieur sans modifier celui-ci.

Exemple :

```text
Vente erronée : −2 douzaines
Correction :    +2 douzaines
Résultat net :   0
```

## 3. Invariants généraux

Les règles suivantes s’appliquent à toutes les opérations.

### 3.1 Transaction atomique

Toutes les écritures produites par une opération doivent réussir ou échouer ensemble.

Une opération ne doit jamais laisser :

- un stock modifié sans mouvement correspondant ;
- une ligne source diminuée sans ligne destination augmentée ;
- un transit créé sans sortie de stock ;
- un transit reçu sans augmentation du stock destination.

### 3.2 Verrouillage

Les lignes de stock existantes concernées doivent être verrouillées avec `select_for_update()` avant le calcul et la modification des quantités.

Lorsque plusieurs lignes sont verrouillées, elles doivent l’être dans un ordre stable, par exemple selon leur clé primaire, afin de réduire les risques de deadlock.

### 3.3 Stock négatif

Chaque compagnie définit sa politique sur les stocks négatifs dans ses paramètres (`Company.accept_negative_stock`).

#### Modification de la politique sur les stocks négatifs

**Avant la V1**: Cette fonctionnalité sera développé pour la V1. Avant son intégration, le stock négatif est bloqué (valeur fixée à `False`, sans possibilité de modification - champs non affiché dans l'UI et en read-only dans l'admin django).

Lorsque la fonctionnalité sera disponible:

- Il est possible de basculer d'un mode à l'autre
- Un rapport de stock négatif est disponible dans le dashboard.

#### Stock négatif bloqué

```text
Une quantité de stock ne peut jamais devenir négative.
```

Toute opération demandant une quantité supérieure au stock disponible est refusée avant l’écriture.

#### Stock négatif accepté

Toute opération demandant une quantité supérieure au stock disponible doit être validée avant l’écriture. Un message d'avertissement s'affiche et demande de confirmer l'opération.

### 3.4 Appartenance à une compagnie

Pour chaque ligne manipulée :

```text
stock.company_id
    = product.company_id
    = location.company_id
    = packaging.company_id
```

Une opération mono-compagnie ne peut jamais introduire une relation entre des objets appartenant à des compagnies différentes.

### 3.5 Compagnie archivée

Aucune opération de stock n’est autorisée pour une compagnie inactive.

Cette règle s’applique également au propriétaire. Une compagnie inactive reste consultable, mais son inventaire est en lecture seule, incluant des produits qui seraient en cours de transit.

### 3.6 Journal immuable

Chaque modification de stock produit une ou plusieurs entrées dans `inventory_movement`.

Le journal conserve au minimum :

- l’opération d’origine ;
- la raison ;
- l’utilisateur ;
- la date ;
- la compagnie ;
- le produit ;
- la location ;
- le conditionnement ;
- la quantité avant ;
- la quantité après ;
- le delta conditionné ;
- le delta en unité de référence ;
- un snapshot des informations historiques pertinentes.

### 3.7 Regroupement des mouvements

Décision proposée : ajouter un identifiant commun, conceptuellement `operation_id`, aux mouvements produits par une même opération.

Exemple de reconditionnement :

```text
operation_id = abc-123

Mouvement 1 : −30 unités
Mouvement 2 : +1 caissette de 30
```

Les deux mouvements demeurent distincts, mais appartiennent à la même transaction métier.

### 3.8 Idempotence

Toute opération pouvant être soumise plusieurs fois doit accepter une clé d’idempotence unique, par exemple un UUID.

```text
Même actor + même compagnie + même idempotency_key
    → une seule opération exécutée
```

Si la même requête est retransmise :

- aucun stock supplémentaire n’est modifié ;
- aucun second mouvement n’est créé ;
- le résultat de la première exécution est retourné.

La protection doit reposer sur une contrainte d’unicité persistante, et non seulement sur une vérification en mémoire.

### 3.9 Erreur

Toute erreur provoque l’annulation complète de la transaction.

Exemples :

- permission manquante ;
- quantité invalide ;
- stock insuffisant ;
- conditionnement incompatible ;
- compagnie inactive ;
- objet hors périmètre ;
- transit dans un mauvais état ;
- conflit d’idempotence ;
- erreur de base de données.

---

# 4. Réception externe

Une réception externe ajoute du stock provenant de l’extérieur du système, par exemple d’un fournisseur.

## Préconditions

- l’utilisateur est actif ;
- la compagnie et la location sont actives ;
- le produit, la location et le conditionnement appartiennent à la même compagnie ;
- le conditionnement est valide pour le produit ;
- la quantité reçue `pack_quantity > 0` ;
- la référence externe, si elle existe, n’a pas déjà été réceptionnée.

## Permission

```text
inventory.stock.purchase
```

La permission doit être valide pour la compagnie et la location destination.

## Verrouillage des lignes

La ligne de stock correspondant à :

```text
company + product + location + packaging
```

est verrouillée si elle existe.

Si elle n’existe pas, sa création doit être protégée par une contrainte d’unicité et par une gestion des créations concurrentes.

## Calcul exact

```text
pack_quantity_init = pack_quantity avant le mouvement pour ce stock_id
          (company_id, product_id, location_id, productpackaging_id)
          0 si l'entrée n'existait pas.
pack_quantity_delta = quantité reçue
pack_quantity_final = pack_quantity_init + pack_delta

ref_quantity_init = pack_quantity_init × packaging.ratio
ref_quantity_final = pack_quantity_final × packaging.ratio
ref_quantity_delta = pack_quantity_delta × packaging.ratio
```

## Stock négatif

Non applicable : La quantité reçue doit être strictement positive.

## Écritures créées

- création ou augmentation d’une ligne `Stock` ;
- création d’un `Movement` ;
  - `location_source` = NULL, `location_dest` = Stock.location_id
  - `productpackaging_source` = NULL, `productpackaging_dest` = Stock.productpackaging
- enregistrement de la référence fournisseur, si disponible (`created_by_comment`) ;
- enregistrement du snapshot et de la clé uuid (idempotence).

## Comportement en cas d’erreur

Aucune ligne de stock ni aucun mouvement n’est créé.

## Stratégie de correction

Une réception erronée est corrigée par un mouvement compensatoire négatif explicitement relié à la réception originale.

La correction est refusée si la quantité reçue n’est plus disponible dans le même conditionnement, sauf si une procédure de correction plus complète est utilisée.

## Idempotence

La référence de réception ou une clé UUID empêche une double réception causée par :

- un double clic ;
- un nouveau scan ;
- une répétition HTTP ;
- une reprise après dépassement de délai.

---

# 5. Vente ou sortie externe

Une vente retire du stock qui quitte le système.

## Préconditions

- l’utilisateur et la compagnie sont actifs ;
- le produit est disponible dans la location et le conditionnement demandés ;
- `pack_quantity > 0` ;
- le stock disponible est suffisant ;
- la vente ou référence externe n’a pas déjà été traitée.

## Permission

```text
inventory.stock.sale
```

ou, pour une raison générique :

```text
inventory.stock.decrease
```

## Verrouillage des lignes

La ligne de stock vendue est verrouillée avant la vérification de sa quantité.

## Calcul exact

```text
pack_delta = −quantité vendue
reference_delta = pack_delta × packaging.ratio

new_pack_quantity = old_pack_quantity + pack_delta
```

La nouvelle quantité doit être supérieure ou égale à zéro.

## Stock négatif

Interdit.

Une vente de 7 caissettes alors que seulement 6 sont disponibles est refusée intégralement.

## Écritures créées

- diminution de la ligne `Stock` ;
- création d’un `Movement` de type `SALE` ;
- snapshot des valeurs avant et après ;
- lien vers la référence de vente, si disponible.
- Si la quantité en stock passe à 0, la quantité est simplement mise à jour à 0. Aucune ligne de stock n'est jamais supprimée

## Comportement en cas d’erreur

Aucune quantité n’est retirée et aucun mouvement n’est créé.

## Stratégie de correction

Une vente enregistrée par erreur est corrigée par un mouvement compensatoire positif.

Ce mouvement ne supprime pas la vente originale et indique la raison de la correction.

## Idempotence

La référence de vente ou une clé UUID empêche la même vente d’être déduite deux fois.

---

# 6. Ajustement d’inventaire

Un ajustement aligne le stock informatique avec un décompte physique.

Deux formes sont possibles :

```text
COUNT_MORE → ajout
COUNT_LESS → retrait
```

## Préconditions

- un décompte physique a été réalisé ;
- la quantité comptée est supérieure ou égale à zéro ;
- l’utilisateur fournit une raison ou un commentaire ;
- la compagnie, la location, le produit et le conditionnement sont cohérents.

## Permission

Selon le résultat :

```text
inventory.stock.count_more
inventory.stock.count_less
```

## Verrouillage des lignes

La ligne concernée est verrouillée avant de comparer la quantité enregistrée à la quantité physique.

## Calcul exact

L’utilisateur fournit la quantité physique finale, et non nécessairement le delta :

```text
delta = counted_pack_quantity − current_pack_quantity
reference_delta = delta × packaging.ratio
```

Si `delta = 0`, aucune modification de stock n’est nécessaire. L’application peut enregistrer séparément le fait qu’un décompte conforme a été réalisé si ce besoin existe.

## Stock négatif

La quantité physique finale ne peut pas être négative.

## Écritures créées

Si le delta est non nul :

- mise à jour de `Stock` ;
- création d’un mouvement `COUNT_MORE` ou `COUNT_LESS` ;
- conservation de la quantité attendue et de la quantité comptée ;
- commentaire ou justification obligatoire.

## Comportement en cas d’erreur

L’ajustement complet est annulé.

Si le stock a changé entre l’ouverture du formulaire et sa validation, la ligne verrouillée est relue et l’application doit demander confirmation plutôt que d’appliquer silencieusement un delta devenu périmé.

## Stratégie de correction

Un ajustement erroné est corrigé par un nouvel ajustement physique ou un mouvement compensatoire autorisé.

## Idempotence

Chaque session de décompte ou soumission possède un identifiant unique.

---

# 7. Emballage

L’emballage transforme une quantité d’un conditionnement source vers un conditionnement destination sans changer la quantité totale en unité de référence.

Exemple :

```text
−60 œufs à l’unité
+5 douzaines
```

## Préconditions

- les deux conditionnements appartiennent au même produit et à la même compagnie ;
- les deux lignes se trouvent dans la même location ;
- les ratios permettent une conversion exacte ;
- la quantité source est disponible ;
- `source_pack_quantity > 0`.

## Permission

```text
inventory.stock.uom_pack
```

Une future convention de nommage pourrait remplacer `uom_pack` par `packaging.pack` pour refléter le modèle actuel.

## Verrouillage des lignes

Les lignes source et destination sont verrouillées dans un ordre stable.

## Calcul exact

Exemple :

```text
source packaging = unité, ratio 1
destination packaging = douzaine, ratio 12
source quantity consumed = 60 unités

reference_quantity_moved = 60 × 1 = 60
destination quantity produced = 60 ÷ 12 = 5 douzaines
```

Invariant :

```text
reference_delta_source + reference_delta_destination = 0
```

Une conversion produisant une fraction interdite de conditionnement est refusée.

## Stock négatif

Interdit sur la ligne source.

## Écritures créées

- diminution du stock source ;
- augmentation ou création du stock destination ;
- deux mouvements reliés par le même `operation_id` ;
- conservation des ratios utilisés au moment de l’opération.

## Comportement en cas d’erreur

Les deux modifications sont annulées.

Il est impossible de diminuer la source sans augmenter la destination.

## Stratégie de correction

L’opération inverse est un déballage. Elle doit référencer l’opération d’emballage originale lorsqu’elle constitue une correction.

## Idempotence

Une clé unique protège l’ensemble de l’opération, et non chaque mouvement séparément.

---

# 8. Déballage

Le déballage transforme un conditionnement en conditionnements plus petits ou en unités de référence.

Exemple :

```text
−1 caissette de 30
+30 œufs à l’unité
```

## Préconditions

- le conditionnement source peut être déballé ;
- le conditionnement destination appartient au même produit ;
- les deux stocks appartiennent à la même compagnie et à la même location ;
- la quantité source est suffisante ;
- la conversion est mathématiquement exacte.

## Permission

```text
inventory.stock.uom_unpack
```

## Verrouillage des lignes

Les lignes source et destination sont verrouillées dans un ordre stable.

## Calcul exact

```text
source = 1 caissette × 30 = 30 œufs
destination = 30 unités × 1 = 30 œufs
```

Invariant :

```text
quantité de référence avant = quantité de référence après
```

## Stock négatif

Interdit sur la ligne source.

## Écritures créées

- diminution du conditionnement source ;
- augmentation du conditionnement destination ;
- deux mouvements partageant le même `operation_id`.

## Comportement en cas d’erreur

L’opération entière est annulée.

## Stratégie de correction

La correction normale est une opération d’emballage inverse, si les produits physiques sont encore disponibles.

## Idempotence

La clé d’idempotence couvre les deux mouvements.

---

# 9. Déplacement interne

Un déplacement interne transfère du stock entre deux sous-locations appartenant à la même racine logistique et à la même compagnie.

## Préconditions

- les locations source et destination sont différentes ;
- elles appartiennent à la même compagnie ;
- elles satisfont la règle métier définissant une relocalisation interne ;
- le produit et le conditionnement restent identiques ;
- la quantité source est suffisante.

## Permission

```text
inventory.stock.relocate
```

La permission doit couvrir les deux locations. Une autorisation sur la source seulement n’est pas suffisante.

## Verrouillage des lignes

Les lignes de stock source et destination sont verrouillées dans un ordre stable.

## Calcul exact

```text
source_pack_delta = −quantity
destination_pack_delta = +quantity

source_reference_delta + destination_reference_delta = 0
```

## Stock négatif

Interdit sur la source.

## Écritures créées

- diminution du stock source ;
- augmentation ou création du stock destination ;
- deux mouvements reliés par le même `operation_id`.

### Décision documentaire à prendre

Le document actuel décrit parfois la relocalisation comme un seul mouvement de delta nul. Or deux lignes `Stock` sont modifiées.

Deux conceptions sont possibles :

1. un événement `Movement` capable de contenir les deux états ;
2. deux écritures de journal reliées à la même opération.

La deuxième solution est plus homogène avec un journal associé à chaque modification de `Stock`.

## Comportement en cas d’erreur

Aucun stock ne quitte la source.

## Stratégie de correction

Effectuer un déplacement inverse relié à l’opération originale.

## Idempotence

Une seule clé protège l’ensemble source–destination.

---

# 10. Création d’un transfert

Un transfert déplace du stock vers une autre location racine ou une autre compagnie en passant par `Transit`.

## Préconditions

- la source et la destination sont identifiées ;
- la source possède la quantité demandée ;
- le produit et le valides ;
- la destination est autorisée ;
- aucun transit identique n’a déjà été créé ;
- la compagnie source est active.

## Permission

Pour un transfert dans la même compagnie :

```text
inventory.stock.transfer_out
```

Pour un transfert inter-compagnies :

```text
inventory.stock.intercompany_out
```

## Verrouillage des lignes

La ligne de stock source est verrouillée.

La destination n’est pas encore augmentée : le stock est physiquement en transit.

## Calcul exact

```text
source_pack_delta = −quantity
reference_quantity_sent = quantity × source_packaging.ratio
```

## Stock négatif

Interdit.

## Écritures créées

Dans la même transaction :

- diminution du stock source ;
- mouvement `TRANSFER_OUT` ou `INTERCOMPANY_OUT` ;
- création du `Transit` ;
- snapshot immuable des informations source ;
- attribution d’un identifiant public de transit ;
- état initial `IN_TRANSIT`.

## Comportement en cas d’erreur

Si le transit ne peut pas être créé, le stock source n’est pas diminué.

## Stratégie de correction

Tant que le transit n’a reçu aucune quantité, il peut être annulé selon les règles de la section « Annulation ».

Après réception partielle ou complète, une correction ou un transfert de retour est nécessaire.

## Idempotence

La création utilise une clé unique. Scanner ou soumettre deux fois l’expédition ne doit créer qu’un transit et une sortie.

---

# 11. Réception partielle d’un transfert

Une réception partielle enregistre seulement une partie de la quantité expédiée.

## Préconditions

- le transit existe ;
- son état est `IN_TRANSIT` ou `PARTIALLY_RECEIVED` ;
- la quantité reçue est strictement positive ;
- la quantité cumulée ne dépasse pas la quantité envoyée ;
- le produit et le conditionnement destination ont été sélectionnés ;
- la compagnie destination est active ;
- l’utilisateur possède l’accès à la location destination.

## Permission

Dans la même compagnie :

```text
inventory.stock.transfer_in
```

Entre deux compagnies :

```text
inventory.stock.intercompany_in
```

## Verrouillage des lignes

Sont verrouillés :

- le transit ;
- la ligne de stock destination, si elle existe.

Le verrouillage du transit empêche deux réceptions simultanées de dépasser la quantité envoyée.

## Calcul exact

Si les conditionnements diffèrent, la comparaison repose sur l’unité de référence :

```text
reference_quantity_received
    = destination_pack_quantity × destination_packaging.ratio
```

Invariant :

```text
cumulative_reference_quantity_received
    ≤ reference_quantity_sent
```

## Stock négatif

Non applicable à la destination.

La quantité restant en transit ne peut pas devenir négative.

## Écritures créées

- augmentation ou création du stock destination ;
- mouvement `TRANSFER_IN` ou `INTERCOMPANY_IN` ;
- augmentation de la quantité cumulée reçue ;
- passage à `PARTIALLY_RECEIVED` s’il reste une quantité ;
- passage à `RECEIVED` si tout a été reçu.

## Comportement en cas d’erreur

Aucune réception partielle n’est conservée.

## Stratégie de correction

Une réception erronée doit produire une correction compensatoire et rétablir explicitement la quantité restant à recevoir.

Cette opération est sensible, car elle modifie à la fois le stock et l’état du transit.

## Idempotence

Chaque événement de réception possède sa propre clé.

Deux réceptions partielles légitimes utilisent deux clés différentes. La répétition de la même clé ne produit aucun ajout supplémentaire.

---

# 12. Réception complète d’un transfert

La réception complète clôt le transit lorsque toute la quantité attendue est reçue.

## Préconditions

Les mêmes préconditions que pour une réception partielle s’appliquent.

La quantité reçue doit correspondre exactement à la quantité restante.

## Permission

```text
inventory.stock.transfer_in
```

ou :

```text
inventory.stock.intercompany_in
```

## Verrouillage des lignes

Le transit et le stock destination sont verrouillés.

## Calcul exact

```text
quantity_received = quantity_remaining
quantity_remaining_after = 0
```

## Stock négatif

Non applicable.

## Écritures créées

- augmentation du stock destination ;
- mouvement d’entrée ;
- état du transit passé à `RECEIVED` ;
- date, utilisateur et commentaire de complétion.

## Comportement en cas d’erreur

Le transit reste dans son état précédent et aucun stock n’est ajouté.

## Stratégie de correction

Un transit reçu n’est pas rouvert silencieusement.

Toute erreur doit être corrigée par une opération explicite conservant la trace de la réception originale.

## Idempotence

Une répétition de la réception complète retourne le résultat existant sans ajouter une seconde fois la quantité.

---

# 13. Annulation

L’annulation empêche une opération non terminée de continuer.

Elle ne supprime jamais un mouvement historique.

## Préconditions

### Transit non expédié

Si un futur état `DRAFT` existe, le transit peut être annulé sans mouvement de stock puisqu’aucune quantité n’a encore quitté la source.

### Transit expédié et non reçu

Un transit `IN_TRANSIT` peut être annulé seulement si :

- aucune quantité n’a été reçue ;
- la marchandise est confirmée comme retournée à la source ;
- la compagnie source peut recevoir la restitution.

### Transit partiellement reçu

Décision proposée :

```text
Une annulation simple est interdite après une réception partielle.
```

Il faut alors traiter séparément la quantité reçue et la quantité restante.

### Transit reçu

Un transit `RECEIVED` ne peut pas être annulé. Il nécessite une correction ou un transfert de retour.

## Permission

Décision à formaliser. Options possibles :

- même permission que l’expédition ;
- permission dédiée comme `inventory.transit.cancel` ;
- owner-only pour certains cas sensibles.

Une permission dédiée est préférable pour l’audit.

## Verrouillage des lignes

Sont verrouillés :

- le transit ;
- le stock source si la quantité doit être restituée.

## Calcul exact

Pour un transit non reçu retourné à la source :

```text
source_pack_delta = +quantity_sent
transit.status = CANCELLED
```

## Stock négatif

Non applicable à la restitution.

## Écritures créées

- mouvement compensatoire d’entrée à la source ;
- restauration du stock source ;
- passage du transit à `CANCELLED` ;
- raison obligatoire ;
- lien vers l’opération d’expédition.

## n’est restitué.

## Stratégie de correction

Une annulation elle-même erronée nécessite une nouvelle opération explicite. L’historique n’est jamais réécrit.

## Idempotence

L’annulation possède une clé unique. Annuler deux fois le même transit ne restitue jamais deux fois le stock.

---

# 14. Correction d’une opération

La correction répare une erreur historique sans modifier le journal existant.

## Préconditions

- l’opération originale existe ;
- elle n’a pas déjà été totalement corrigée ;
- la correction indique une raison obligatoire ;
- l’utilisateur possède la permission requise ;
- la correction n’introduit aucun stock négatif ;
- tous les objets nécessaires sont encore accessibles.

## Permission

Décision proposée : utiliser une permission dédiée à haute sensibilité, par exemple :

```text
inventory.movement.correct
```

Cela évite qu’une simple permission de vente autorise implicitement la correction de tout mouvement historique.

## Verrouillage des lignes

Toutes les lignes de stock affectées par l’opération compensatoire sont verrouillées.

L’opération originale ou son enregistrement de regroupement est également verrouillé afin d’empêcher deux corrections concurrentes excessives.

## Calcul exact

Une correction complète applique l’inverse des deltas originaux :

```text
correction_delta = −original_delta
```

Une correction partielle doit préciser la quantité corrigée et ne peut pas dépasser la quantité originale restant à corriger.

## Stock négatif

Interdit.

Exemple : une réception de 10 unités ne peut pas être entièrement annulée si 8 unités ont déjà été vendues et qu’il n’en reste que 2 dans le stock concerné.

## Écritures créées

- un ou plusieurs mouvements compensatoires ;
- un nouvel `operation_id` ;
- une relation vers l’opération corrigée ;
- la quantité corrigée ;
- l’acteur, la date et la justification ;
- aucune modification du mouvement original.

## Comportement en cas d’erreur

Aucune correction partielle n’est conservée.

## Stratégie de plusieurs corrections cumulées de dépasser l’opération originale.

---

# 15. Machine d’état proposée pour `Transit`

```text
DRAFT
  │
  │ expédition
  ▼
IN_TRANSIT
  │
  ├── réception partielle ──> PARTIALLY_RECEIVED
  │                              │
  │                              ├── autre réception partielle
  │                              │       └──> PARTIALLY_RECEIVED
  │                              │
  │                              └── réception du solde
  │                                      └──> RECEIVED
  │
  ├── réception complète ──> RECEIVED
  │
  └── annulation autorisée ──> CANCELLED
```

Transitions autorisées :

| État courant         | Opération                 | Nouvel état          |
| -------------------- | ------------------------- | -------------------- |
| `DRAFT`              | Expédier                  | `IN_TRANSIT`         |
| `DRAFT`              | Annuler                   | `CANCELLED`          |
| `IN_TRANSIT`         | Réception partielle       | `PARTIALLY_RECEIVED` |
| `IN_TRANSIT`         | Réception complète        | `RECEIVED`           |
| `IN_TRANSIT`         | Annuler et restituer      | `CANCELLED`          |
| `PARTIALLY_RECEIVED` | Réception partielle       | `PARTIALLY_RECEIVED` |
| `PARTIALLY_RECEIVED` | Réception du solde        | `RECEIVED`           |
| `RECEIVED`           | Aucune transition directe | État final           |
| `CANCELLED`          | Aucune transition directe | État final           |

Les corrections n’effacent pas une transition. Elles créent une nouvelle opération métier et une nouvelle trace d’audit.

---

# 16. Décisions encore ouvertes

Les points suivants doivent être confirmés avant de considérer ce document comme normatif :

1. `pack_quantity` est-elle obligatoirement entière pour les conditionnements physiques ?
2. La quantité de référence est-elle calculée ou stockée ?
3. Un mouvement représente-t-il une modification unique de `Stock` ou une opération complète ?
4. Faut-il introduire un modèle parent comme `InventoryOperation` pour regrouper les mouvements ?
5. Quel comportement adopter lorsque les ratios produisent des fractions ?
6. Le stock négatif est-il toujours interdit ?
7. Une réception externe partielle existe-t-elle sans futur modèle de commande fournisseur ?
8. Quelles permissions permettent l’annulation et la correction ?
9. Une compagnie inactive peut-elle recevoir un transit déjà expédié ?
10. Comment traiter une perte ou un écart constaté pendant le transport ?
11. La quantité envoyée est-elle comparée à la quantité reçue exclusivement en unité de référence ?
12. Peut-on rouvrir un transit complété, ou seulement le corriger par compensation ?

La décision structurante que je recommande est d’introduire conceptuellement une opération parent regroupant les mouvements. `Movement` resterait une écriture élémentaire immuable, tandis que l’opération exprimerait l’intention métier complète : vente, reconditionnement, transfert ou correction. Cela rendrait l’atomicité, l’idempotence et les corrections beaucoup plus faciles à représenter.