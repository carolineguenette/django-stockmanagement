
"""
Jalons du projet :
------------------
0.0.x : Phase de développement initiale (pré-POC)
0.1.x : POC (Proof of Concept)
        Validation de l'architecture multi-tenant et de l'isolation
        des données par entreprise.
0.2.x : MVP (Minimum Viable Product)
        Mise en œuvre de la valeur métier brute : gestion sécurisée
        des stocks et des mouvements d'inventaire.
0.3.x à 0.9.x : Next
        Ajouts incrémentiels de couches de fonctionnalités.
        Un tag (ex: 0.3.0-notifications) sera utilisé pour décrire
        la fonctionnalité majeure implémentée.
1.0   : V1
        Première version finale incluant tous les éléments
        du cahier des charges.
> 2.0: Future (VX)
        Versions futures pour les fonctionnalités prévues durant la conception
        mais non prévues dans le développement actuel.
"""
# Présentement utilisé par
#   .github/workflows/test.yml, qui extrait cette variable pour le badge du README.md.
#   affichage de la version dans l'UI (config/settings.py -> PROJECT_VERSION = __version__ -> envoyé au main context pour l'affichage)
# TODO Quand sera rendu à 1.0 et premier release, utiliser tag Git à la place d'une version en dure.
__version__ = "0.0.2"