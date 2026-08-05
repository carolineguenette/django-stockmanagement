![Statut](https://img.shields.io/badge/Statut_du_document-OLD_Conserver_pour_revision_avant_suppression-purple.svg)

## Conception & choix techniques

# Choix techniques

Projet Gestion de stocks — document de synthèse des choix structurants

## Décisions validées

- Le projet est recentré sur un modèle propriétaire global.
- Plusieurs utilisateurs peuvent être propriétaires.
- Le statut propriétaire est porté par `User.is_owner`.
- Aucun rôle RBAC `Owner` n'est créé.
- Seul un propriétaire peut créer un autre propriétaire.
- Il doit toujours exister au moins un propriétaire actif.
- Les employés sont gérés par le RBAC custom.
- Un employé peut créer d'autres employés s'il possède la permission appropriée.
- Un employé ne peut jamais créer ou modifier un propriétaire.
- Les URLs `/c/<company_slug>/...` sont filtrées par compagnie courante.
- Les vues globales `/owner/...` sont réservées aux propriétaires.
- Un `CompanyScopedManager` sera créé.
- Le middleware de contexte compagnie est nommé `CompanyMiddleware`.
- L'app transversale de scope est nommée `scope`.

## 1. Framework principal

Le projet utilise Django comme framework web principal.

Django est conservé pour :

- son ORM ;
- son système d'authentification ;
- ses migrations ;
- son administration technique ;
- son écosystème ;
- son intégration avec les tests automatisés.

## 2. Authentification et identité

Django Auth est utilisé pour l'identité utilisateur et l'infrastructure d'authentification :

- utilisateur ;
- mot de passe ;
- sessions ;
- login/logout ;
- `is_active` ;
- `is_staff` ;
- `is_superuser`.

Les permissions métier ne sont pas gérées par `auth_group` ou `auth_permission`.

## 3. Permissions métier custom

Les permissions métier sont gérées par l'application `access`.

Cette décision permet de représenter explicitement :

- les rôles employés ;
- les permissions par compagnie ;
- les permissions par location ;
- les droits de gestion d'employés ;
- les règles métier propres à l'inventaire.

Le propriétaire métier n'est pas représenté par un rôle RBAC. Il est identifié par `users.User.is_owner`.

## 4. Modèle propriétaire global

Le projet est recentré sur le scénario principal du cahier des charges :

> une même instance applicative permet à un ou plusieurs propriétaires de gérer plusieurs entreprises leur appartenant.

Conséquences :

- toutes les compagnies présentes en base appartiennent au même périmètre propriétaire global ;
- un utilisateur `is_owner=True` peut accéder aux données de toutes les compagnies ;
- les employés sont limités par le RBAC custom ;
- les vues globales owner sont séparées des vues company-scoped.

## 5. Scope compagnie

Les vues liées à une compagnie utilisent le format :
