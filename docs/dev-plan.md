<div align="center">

<img src="../assets/img/logo.svg" alt="Logo Gestion de stocks" width="60" />

# Plan de développement

<img src="https://img.shields.io/badge/Statut_du_document-Document_vivant_(plan_de_route)-purple.svg" alt="Statut" /> [![Schema](https://img.shields.io/badge/Gestion_du_projet-Jira-blue.svg)](https://solution-cg.atlassian.net/jira/software/c/projects/SD/list)

</div>

## Migration vers JIRA 

Pour ce projet portfolio, j'ai mis en place une gestion sous Jira en combinant une approche par Versions (Releases) et des Sprints axés sur des livrables fonctionnels. Je l'utilise notamment pour estimer la charge de travail et analyser le ratio temps estimé vs temps réel passé. Le tout est ouvert au public en consultation.

[Accéder au Tableau de bord Jira et backlog en direct](https://solution-cg.atlassian.net/jira/software/c/projects/SD/list) (À noter que Jira est un peu capricieux avec les utilisateurs non connectés, malgré la configuration adéquate des permissions)

---

### Jalons du projet


| Étape      | Description                                                                                                                                                                                                                                      |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 0.1 POC     | Proof of Concept testant l'architecture multi-tenant et surtout l'isolation des données par entreprises                                                                                                                                         |
| 0.2 MVP     | Minimal Viable Product mettant en oeuvre la valeur métier brute: gérer du stock et des mouvements d'inventaire de manière sécurisée                                                                                                         |
| 0.3 Next    | Déclinaision de versions 0.3 à 0.9 qui ajoute des couches de fonctionnalités de manière incrémentielle, jusqu'à arriver à la version V1. Un tag (remplaçant "NEXT") sera donné pour décrire la fonctionnalité majeure implémentée. |
| 1.0 V1      | Première version incluant tous les éléments du cahier des charges                                                                                                                                                                             |
| Future (VX) | Version future (fonctionnalités non prévues dans le développement pour le moment)

### Automatisation GitHub <-> Jira

GitHub et Jira communiquent via des *automations*. Ces automations permettent de synchroniser automatiquement des informations entre les deux plateformes, facilitant ainsi le suivi des tâches et la gestion du projet.

Pour qu'un git commit soit associé à un ticket Jira, il faut que le message de commit contienne la clé du ticket (**Ex: SD-1**).

#### Trois automations ont été créées.

* Quand un 1er commit est effectué --> Déplacer le ticket vers la colonne "En cours"
* Quand le message de commit contient "-TEST" --> Déplacer le ticket vers la colonne "En test"
  * **Ex: git commit -m "SD-1-TEST: fonctionnalité dont on est en train d'écrire les pytests..."
* Quand une pull request est mergée -> déplacer le ticket vers la colonne "Terminé"
