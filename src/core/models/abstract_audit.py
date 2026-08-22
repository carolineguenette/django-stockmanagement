from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class AbstractAudit(models.Model):
    """
    Modèle abstrait pour faciliter l'ajout de champs d'audit
    aux différents modèles de l'application.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Create at")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Update at")
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="%(app_label)s_%(class)s_created",
        verbose_name=_("Created by")
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="%(app_label)s_%(class)s_updated",
        verbose_name=_("Updated by")
    )

    def save(self, *args, **kwargs):
        # Récupération sécurisée de l'utilisateur stocké par le middleware django
        from src.core.middleware import get_current_user
        user = get_current_user()

        # Si l'utilisateur est connecté (et pas anonyme)
        if user and user.is_authenticated:
            if not self.pk:  # Création d'un nouvel enregistrement
                self.created_by = user
                self.updated_by = None  # Reste explicitement null à la création
            else:            # Mise à jour d'un enregistrement existant
                self.updated_by = user

        super().save(*args, **kwargs)

    class Meta:
        abstract = True
