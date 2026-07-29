<div align="center">

<img src="../assets/img/logo.svg" alt="Logo Gestion de stocks" width="60" />

# Plan de développement

![Statut](https://img.shields.io/badge/Statut_du_document-Document_vivant_(plan_de_route)-purple.svg)

<h3>
  <a href="#current">Étape courante</a> | 
  <a href="#backlog">Backlog</a>
</h3>

</div>

## Migration vers JIRA 

Pour ce projet portfolio, j'ai mis en place une gestion sous Jira en combinant une approche par Versions (Releases) et des Sprints axés sur des livrables fonctionnels. Je l'utilise notamment pour estimer la charge de travail et analyser le ratio temps estimé vs temps réel passé. Le tout est ouvert au public en consultation.

[Accéder au Tableau de bord Jira et backlog en direct](https://solution-cg.atlassian.net/jira/software/c/projects/SD/list) (À noter que Jira est un peu capricieux avec les utilisateurs non connectés, malgré la configuration adéquate des permissions)

---
> [!WARNING]
> OLD - En cours de migration vers JIRA

# Introduction

Ce plan de développement fait office de feuille de route centralisant l'avancement du projet. Il permet aussi de prioriser les tâches selon une approche itérative (POC, MVP, V1).

### Jalons du projet


| Étape      | Description                                                                                                                                                                                                                                      |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 0.1 POC     | Proof of Concept testant l'architecture multi-tenant et surtout l'isolation des données par entreprises                                                                                                                                         |
| 0.2 MVP     | Minimal Viable Product mettant en oeuvre la valeur métier brute: gérer du stock et des mouvements d'inventaire de manière sécurisée                                                                                                         |
| 0.3 Next    | Déclinaision de versions 0.3 à 0.9 qui ajoute des couches de fonctionnalités de manière incrémentielle, jusqu'à arriver à la version V1. Un tag (remplaçant "NEXT") sera donné pour décrire la fonctionnalité majeure implémentée. |
| 1.0 V1      | Première version incluant tous les éléments du cahier des charges                                                                                                                                                                             |
| Future (VX) | Version future (fonctionnalités non prévues dans le développement pour le moment)
