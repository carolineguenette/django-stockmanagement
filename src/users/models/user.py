from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from src.users.choices import PreferredHomePageChoices


class User(AbstractUser):
    # id est déjà inclus nativement par Django comme AutoField/BigIntergerField PK
    # password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined sont natifs

    is_owner = models.BooleanField(default=False)

    # Stockage de la langue préférée de l'utilisateur
    preferred_language = models.CharField(
        max_length=5, default="fr", verbose_name=_("preferred language")
    )

    preferred_home_page = models.CharField(
        max_length=20,
        choices=PreferredHomePageChoices.choices,
        default=PreferredHomePageChoices.DASHBOARD,
    )

    class Meta:
        db_table = 'users_user'
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"
