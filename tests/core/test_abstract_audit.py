import pytest
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from typing import Callable

from src.core.models.abstract_audit import AbstractAudit
from src.core.middleware import AuditUserMiddleware

# Récupération dynamique du modèle Utilisateur configuré dans le projet (AUTH_USER_MODEL)
User = get_user_model()


# --- Modèle temporaire pour tester la classe abstraite ---
class DummyAuditModel(AbstractAudit):
    """Modèle concret fictif servant uniquement à valider AbstractAudit."""
    name = models.CharField(max_length=50)

    class Meta:
        # Indique à Django de ne pas tenter de le migrer globalement
        app_label = 'core'


@pytest.fixture(autouse=True)
def setup_dummy_table():
    """Crée la table en mémoire au début du test et la détruit à la fin."""
    from django.db import connection
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(DummyAuditModel)
    yield
    with connection.schema_editor() as schema_editor:
        schema_editor.delete_model(DummyAuditModel)


@pytest.mark.django_db(transaction=True)   # Car on va faire un CREATE TABLE et MySQL ne sait pas faire un rollback sur ça. Ça évite l'erreur de sécurité de django ET force django à faire un DROP à la fin du test.
class TestAbstractAuditAndMiddleware:

    @pytest.fixture
    def user(self):
        """Fixture pour créer un utilisateur de test."""
        return User.objects.create_user(username="testuser", password="password123")

    @pytest.fixture
    def factory(self):
        """Fixture pour générer de fausses requêtes HTTP."""
        return RequestFactory()

    def _execute_with_middleware(self, user: AbstractUser, factory: RequestFactory,
                                 callback_action: Callable[[], None]) -> None:
        """
        Fonction utilitaire qui simule le passage dans le middleware
        et exécute une action de sauvegarde PENDANT le traitement.
        """
        request = factory.get('/')
        request.user = user

        # On injecte l'action de sauvegarde directement dans la réponse simulée
        def mock_get_response(req):
            callback_action()  # La sauvegarde s'exécute ICI, avant le nettoyage !
            return None

        # On passe cette fonction personnalisée au middleware
        middleware = AuditUserMiddleware(mock_get_response)

        # Le middleware capture l'utilisateur dans le Thread Local durant le __call__
        middleware(request)


    def test_create_record_sets_created_by_and_leaves_updated_by_null(self, user, factory):
        """Vérifie que la création d'un enregistrement définit created_by et laisse updated_by à NULL."""
        obj = DummyAuditModel(name="Nouveau Produit")

        # Sauvegarde simulée à travers le cycle de vie du middleware
        def action():
            obj.save()

        self._execute_with_middleware(user, factory, action)

        # Assertions
        assert obj.created_by == user
        assert obj.updated_by is None
        assert obj.created_at is not None

    def test_update_record_sets_updated_by(self, user, factory):
        """Vérifie qu'une modification ultérieure remplit updated_by sans modifier created_by."""
        obj = DummyAuditModel(name="Produit Initial")

        # 1. Création initiale
        self._execute_with_middleware(user, factory, obj.save)

        # 2. Création d'un second utilisateur pour simuler une modification par quelqu'un d'autre
        other_user = User.objects.create_user(username="editoruser", password="password123")

        # Modification de l'objet
        obj.name = "Produit Modifié"

        # Sauvegarde simulée avec le second utilisateur
        def action_update():
            obj.save()

        self._execute_with_middleware(other_user, factory, action_update)

        # Assertions
        assert obj.created_by == user  # L'auteur initial ne doit pas changer
        assert obj.updated_by == other_user  # Le modificateur doit être mis à jour
        assert obj.updated_at >= obj.created_at
