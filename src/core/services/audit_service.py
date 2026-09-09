# src/core/services/audit_service.py
from contextvars import ContextVar
from typing import Optional
from django.contrib.auth import get_user_model

# Variable de contexte isolée, compatible Thread et Async
_user_context: ContextVar[Optional[get_user_model()]] = ContextVar('current_user', default=None)

class AuditService:
    """Service gérant le contexte utilisateur pour l'audit"""

    @classmethod
    def set_user(cls, user):
        # Return du token généré par Python, pour le reset_user
        return _user_context.set(user)

    @classmethod
    def reset_user(cls, token):
        # Nettoyage du contexte
        _user_context.reset(token)

    @classmethod
    def get_current_user(cls):
        return _user_context.get()

    @classmethod
    def apply_audit(cls, obj, user=None):
        """Applique les champs d'audit sur un objet avant sa sauvegarde"""
        current_user = user or cls.get_current_user()

        if current_user and current_user.is_authenticated:
            if not obj.pk:  # Création
                obj.created_by = current_user
                obj.updated_by = None
            else:           # Modification
                obj.updated_by = current_user
