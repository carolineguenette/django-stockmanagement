import pytest


def test_infrastructure_minimal():
    """Un test simple pour valider que le moteur de test tourne."""
    assert 1 == 1


@pytest.mark.django_db
def test_acces_base_de_donnees():
    """Valide que pytest-django initialise, écrit et lit dans la base de données de test."""
    from django.contrib.auth import get_user_model

    User = get_user_model()

    # 1. On mémorise le nombre d'utilisateurs au départ de CE test (garanti à 0 ici, mais bonne pratique)
    nb_utilisateurs_depart = User.objects.count()

    # 2. On crée un utilisateur temporaire en mémoire de test
    User.objects.create_user(username="testeur_infra", password="password123")

    # 3. On vérifie que le compteur a bien augmenté de exactement 1
    assert User.objects.count() == nb_utilisateurs_depart + 1
