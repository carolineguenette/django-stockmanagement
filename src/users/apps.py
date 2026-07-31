from django.apps import AppConfig

# Cette application gère l'utilisateur personnalisé étendant AbstractUser ainsi que la gestion des rôles pour le POC.

class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "src.users"
