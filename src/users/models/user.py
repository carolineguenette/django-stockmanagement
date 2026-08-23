from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from src.users.choices import PreferredHomePageChoices, PreferredLanguageChoices

class User(AbstractUser):
    # id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active sont natifs.

    is_owner = models.BooleanField(
        default=False,
        verbose_name=_("Owner status"),
        help_text=_(
            "Designates that this user is a company owner. He has all front-end permissions on his companies without explicitly assigning them."
        ),
    )

    photo = models.ForeignKey(
        'core.Image',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users_photos",
        verbose_name=_("Photo"),
    )

    # -------------------------------
    # Champs d'audit
    # Note : Django a déjà 'date_joined' natif (DateTimeField auto_now_add) qui correspond à 'created_at'.
    # -------------------------------
    
    update_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    created_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users_created",
        verbose_name=_("Created by"),
    )

    updated_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users_updated",
        verbose_name=_("Updated by"),
    )

    # -------------------------------
    # Champs de préférences
    # -------------------------------
    
    preferred_language = models.CharField(
        max_length=10,
        verbose_name=_("Preferred language"),
        choices=PreferredLanguageChoices.choices,
        default=PreferredLanguageChoices.DEFAULT,
    )

    preferred_home_page = models.CharField(
        max_length=20,
        verbose_name=_("Preferred home page"),
        choices=PreferredHomePageChoices.choices,
        default=PreferredHomePageChoices.DASHBOARD,
    )

    preferred_company = models.ForeignKey(
        "company.Company",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="preferred_by_users",
        verbose_name=_("Preferred company"),
    )

    # --- RBAC: évite la création automatique des tables natives 'groups' et 'user_permissions'
    #     de django qui ne sont pas utilisées (remplacées par RBAC personnalisé) ---
    groups = None
    user_permissions = None

    class Meta:
        db_table = "users_user"
        verbose_name = _("user")
        verbose_name_plural = _("users")

    # Surcharge de la méthode save pour automatiser l'audit utilisateur via le middleware
    def save(self, *args, **kwargs):
        from src.core.middleware import get_current_user

        current_user = get_current_user()

        if current_user and current_user.is_authenticated:
            if not self.pk:  # Création d'un nouvel utilisateur
                self.created_by = current_user
                self.updated_by = None
            else:  # Mise à jour d'un utilisateur existant
                self.updated_by = current_user

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"
