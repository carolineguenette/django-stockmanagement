<div align="center">

<img src="../assets/img/logo.svg" alt="Logo Gestion de stocks" width="60" />

# Analyse technique et synthèse des choix structurants

Projet Gestion de stocks — document de conception

![Statut](https://img.shields.io/badge/Statut_du_document-En_cours_de_rédaction-purple.svg)

<h3>

[Framework](#framework) | [Authentification et identité](#auth) | [SGDB](#sgdb) | [Shared DB](#shared-db)  | [Analyse RBAC](#analysis) | [Recherches](#recherches)

</h3>

</div>

Ce fichier présente les analyses réalisées et justifie rationnellement les choix techniques et architecturaux fait.

[← Conception](2-conception.md) | [README](../README.md) |  [Sécurité →](4-data-security.md)

---

## Framework principal <a id="framework"></a>

Le projet utilise Django comme framework web principal.

Django est conservé pour :

- son ORM ;
- son système d'authentification ;
- ses migrations ;
- son administration technique ;
- son écosystème ;
- son intégration avec les tests automatisés.

---

## Authentification <a id="auth"></a>

Django Auth est utilisé pour l'identité utilisateur et l'infrastructure d'authentification :

- utilisateur ;
- mot de passe ;
- sessions ;
- login/logout ;
- AbstractUser (dont `is_active`, `is_staff` et `is_superuser`).

Les permissions métier ne sont pas gérées par `auth_group` ou `auth_permission`. La section suivante documente le cheminement menant à ce choix.

---

## Choix du moteur de base de données SGDB <a id="sgdb"></a>

Un premier jet de code a été réalisé rapidement en configurant MySQL, déjà fonctionnel sur un environnement de développement local WSL.

Bien que **PostgreSQL** soit souvent la référence pour des projets SaaS dépassant le simple CRUD en raison de ses fonctions d'isolation (RLS) et sa robustesse, le choix choix de **MySQL** se justifie pleinement par :

1. **L'agrégation multi-entreprises :** Sous MySQL, les données partagées facilitent les agrégations SQL natives pour les tableaux de bord Chart.js.
2. **L'approche pédagogique :** Coder  la sécurité par ligne (Row-level) via un middleware et un Manager Django compense l'absence de RLS native de MySQL et permet de démontrer une certaine maîtrise technique pour un projet portfolio.
3. **L'environnement existant :** Le gain de temps immédiat pour le POC.

---

## Analyse des risques de l'architecture "Shared Database" et atténuations <a id="shared-db"></a>

Le choix d'une base de données unique et partagée (Shared Database, Shared Schema) avec isolation logicielle simplifie grandement les agrégations multi-entreprises. Cependant, ce modèle introduit des risques techniques critiques en production. Voici comment le projet y fait face :

### A. Le risque du "Voisin Bruyant" (Noisy Neighbor Effect)
* **Le problème** : Si une entreprise cliente (ex: un très gros entrepôt) génère des millions de mouvements de stock ou de requêtes, elle peut saturer le CPU et les Entrées/Sorties (I/O) du serveur MySQL. Cela ralentira l'application pour *toutes* les autres entreprises hébergées sur la plateforme.
* **Stratégie d'atténuation (V1 & Évolution)** :
  1. **Index composites systématiques** : Toutes les tables clés (produits, stocks, mouvements) possèdent un index composite combinant `company_id` et l'identifiant de la ressource. MySQL effectue ainsi un filtrage immédiat au niveau de l'index sans scanner les lignes des autres entreprises.
  2. **Limitation de débit (Rate Limiting)** : (Évolution future) Implémentation de restrictions au niveau des middlewares Django pour bloquer les abus d'API par entreprise.

### B. Concurrence et verrous sur les stocks (Race Conditions)
* **Le problème** : Dans un système de stock partagé, si deux employés d'une même entreprise valident une commande pour le même produit exactement au même millième de seconde, les deux requêtes de mise à jour de quantité (`UPDATE`) vont s'affronter. Cela peut mener à des erreurs de calcul (stock négatif) ou à des blocages de base de données (*Deadlocks*).
* **Stratégie d'atténuation** :
  1. **Utilisation de `select_for_update()`** : Les vues et services Django responsables de la modification des stocks utiliseront le verrouillage pessimiste de l'ORM. MySQL verrouillera la ligne de la table `inventory_stock` concernée le temps que la transaction se termine, forçant la deuxième requête à attendre son tour en toute sécurité.
  2. **Mises à jour atomiques** : Utilisation des expressions `F()` de Django (ex: `stock.quantity = F('quantity') - 1`) pour laisser MySQL gérer l'opération mathématique directement au moment du verrou, évitant de lire une donnée périmée en mémoire Python.

### C. Risque de fuite de données par erreur humaine (Data Leakage)
* **Le problème** : Le cloisonnement reposant entièrement sur le code applicatif (`CompanyScopedManager`), l'oubli d'un filtre ou l'utilisation d'une requête SQL brute (`raw()`) non sécurisée par un développeur pourrait exposer le stock d'une entreprise A à une entreprise B.
* **Stratégie d'atténuation** :
  1. **Tests unitaires automatisés systématiques** : Mise en place d'une suite de tests (pytest) qui simule une requête avec le compte de l'Entreprise A et tente explicitement d'accéder à l'ID d'un produit de l'Entreprise B, validant qu'un code HTTP 404 ou une exception ORM est levée à chaque fois.


---

## Analyse RBAC <a id="analysis"></a>

[Django RBAC Natif](#django-rbac-natif) | [Besoins](#besoins) | [Django-guardien](#django-guardien) | [Django-tenants](#django-tenants) | [Choix du SGDB](#sgdb) | [Conclusion](#conclusion)

### Django RBAC Natif

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

### Besoins RBAC pour l'application de Gestion de Stocks <a id="besoins"></a>

En plus du comportement CRUD standard, cette application de gestion de stocks multi-entreprises impose des contraintes de sécurité spécifiques :

* **Isolation par Entreprise (`Company`):** Un utilisateur possède des permissions distinctes pour chaque entreprise.
  * *Exemple* : un utilisateur peut être *Gestionnaire* et *Vendeur* dans l'Entreprise A et disposer uniquement d'un rôle en *Lecture seule* dans l'Entreprise B.
* **Permissions granulaires**: Certaines permissions ne s'alignent pas sur le modèle CRUD global.
  * *Exemple 1 (Métier)* : Un vendeur a le droit de diminuer l'inventaire lors d'une vente, mais n'a pas le droit de déclarer une perte par bris, ni d'augmenter le stock. Le droit est lié au contexte du mouvement et non au simple droit de modification (`change_stock`) du modèle.
  * *Exemple 2 (Interface)* : un gestionnaire a accès aux graphiques d'alerte de seuil bas mais pas aux graphiques globaux qui rassemblent les données de plusieurs entreprises.
* **Besoin d'aggrégation de données multi-entreprises** : il faut également penser au futur dashboard qui doit rassembler les données de plusieurs entreprises dans une vue résumé, avec des graphiques chart.js.

#### Limitation Django

Les permissions natives CRUD de Django lient l'utilisateur et le modèle globalement. Ainsi, le systeme natif de Django ne peut pas, tel quel, répondre aux besoins concernant l'**Isolation par Entreprise** ou les **Permissions granulaires**.

### RBAC de librairies tierces

Des librairies django existent pour répondre spécifiquement aux besoins de développement d'application django multi-tenant.

#### Django-guardien

Django-guardian permet d'étendre le système de permissions natif de django afin d'assigner des droits sur des instances précises


| Avantages                                                                                                                                                                                  | Inconvénients                                                                                                                                                                                                                              |
| :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Granularité extrême** : Permet d'assigner des permissions spécifiques à un utilisateur pour un objet unique (ex: "Julie peut modifier le stock du Produit A mais pas du Produit B"). | **Lourdeur SQL** : Chaque vérification de permission nécessite des jointures complexes ou des requêtes supplémentaires, ce qui peut dégrader les performances à grande échelle                                                       |
| **Interface Admin intégrée** : Ajoute des vues de gestion des permissions directement dans l'interface d'administration de Django.                                                       | **Surcouche inutile pour le besoin actuel** : Pour le projet de gestion de stocks, le besoin est d'avoir des droits fonctionnels (ex: stock.sale) plutôt que des droits par objet individuel. Guardian serait "overkill" dans ce contexte. |
| **Efficacité pour peu de modèles** : C'est une solution robuste pour des permissions par objet sur un ou deux modèles critiques.                                                        | **Complexité de maintenance** : La gestion des tables de permissions génériques (GenericForeignKey) rend le débogage et la maintenance de la base de données plus ardus.                                                               |

#### Django-tenants

Django-tenants implémente le multi-tenancy en créant des schémas de base de données distincts pour chaque entreprise, en isolant par schémas PostGreSQL.


| Avantages                                                                                                                                                                    | Inconvénients                                                                                                                                                                                                                                                   |
| :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Isolation de données maximale** : Le cloisonnement au niveau du SGBD garantit qu'un bug applicatif ne peut pas faire fuiter les données d'une entreprise vers une autre. | **Cauchemar des statistiques globales** : Les requêtes croisées entre entreprises (comme pour un dashboard consolidé inter-entreprises pour un propriétaire) sont extrêmement complexes et lentes car elles nécessitent de basculer de schéma en schéma. |
| **Code métier "propre"**: Puisque l'isolation est gérée par le schéma, il n'est pas nécessaire d'ajouter manuellement .filter(company=...) à toutes les requêtes.     | **Incompatibilité MySQL** : Cconçu exclusivement pour PostgreSQL car MySQL ne supporte pas nativement les schémas de la même manière.                                                                                                                       |
| **Sauvegardes indépendantes** : Il est plus simple d'exporter ou de restaurer les données d'un seul client spécifique.                                                    | **Migrations chronophages** : Chaque migrate doit être exécuté sur chaque schéma client. Avec des dizaines d'entreprises, cela devient un processus très lourd.                                                                                             |

Ces bibliothèques Django visent à résoudre les limites du RBAC natif de dnango, mais elles s'avèrent inadaptées à l'architecture MySQL et les besoins d'agrégation. **Django-Guardian** offre une granularité par objet mais impose une complexité SQL inutile pour des droits fonctionnels. De son côté, **Django-Tenants** assure une isolation forte via des schémas PostgreSQL, mais cette approche est techniquement incompatible avec MySQL et rend les calculs statistiques multi-entreprises (nécessaires au dashboard propriétaire) extrêmement inefficaces.

### Conclusion

Pour répondre aux exigences d'**Isolation par Entreprise**, de **Permissions granulaires**, le système natif RBAC de Django ne suffit pas. Au vu des objectifs pédagogiques du projet et de la nécessité de produire des rapports consolidés performants via Chart.js, l'utilisation de solutions de librairie tierce sont également écartées.

La solution retenue est de concevoir et coder un système RBAC personnalisé utilisant une architecture de base de données partagée. Pour prévenir tout risque de fuite de données, cette approche sera sécurisée par des garde-fous rigoureux : un middleware injectant systématiquement le contexte de l'entreprise et un Manager personnalisé filtrant automatiquement tous les QuerySets.

---

## Recherches sur les logiciels existants en Gestion d'inventaire <a id="recherches"></a>

Plusieurs heures ont été investies sur la compréhension des besoins métier et les logiciels existants en gestion d'inventaire. 