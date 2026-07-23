from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    # Stockage de la langue préférée de l'utilisateur
    preferred_language = models.CharField(
        max_length=5,
        default='fr',
        verbose_name=_("Langue préférée")
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"
