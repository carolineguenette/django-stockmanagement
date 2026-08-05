<div align="center">

<img src="../assets/img/logo.svg" alt="Logo Gestion de stocks" width="60" />

# Django Urls

Projet Gestion de stocks — document de travail

![Statut](https://img.shields.io/badge/Statut_du_document-En_cours_de_rédaction-purple.svg)
![](https://img.shields.io/badge/Unique-company__id,_slug-blueviolet.svg)

</div>

Ce document détaille la structure prévue des urls, incluant la page d'accueil, les pages ouvertes à tous (pages liées à l'authentification), la gestion des traductions de l'UI, la zone tableau de bord et les section nécessitant une entreprise active.

| Contexte         | Comportement                                     |
|:---------------- |:------------------------------------------------ |
| /c/company-a/.,, | filtre sur company-a                             |
| /global/...      | requêtes globales explicites                     |
| aucun contexte   | Erreur / Refus sur les modèles company-scoped    |
| Django-admin     | Accès via manager spécial ou all_objects réservé |
