from django.db import models
from django.utils.translation import gettext_lazy as _

class PreferredHomePageChoices(models.TextChoices):
    # Format : CLÉ_BD = "valeur_bd", _("Libellé Traduit")
    DASHBOARD = "dashboard", _("Dashboard")         # type: ignore - car linter ne gère pas le _() de type StrPromise (avertissement)
    INVENTORY = "inventory", _("Inventory")         # type: ignore
    SCANNER   = "scanner", _("Barcode scanner")     # type: ignore
    DEBUG     = "debug", "Debug"

    @property
    def route_name(self) -> str:
        """
        Associe dynamiquement chaque clé de base de données à sa route Django.
        """
        mapping = {
            PreferredHomePageChoices.DASHBOARD: "reporting:dashboard",
            PreferredHomePageChoices.INVENTORY: "catalogue:product_list",
            PreferredHomePageChoices.SCANNER:   "inventory:barcode_scanner",
            PreferredHomePageChoices.DEBUG:     "core:home_debug",
        }
        # Retourne la route associée, ou une route par défaut sécuritaire
        return mapping.get(self, "reporting:dashboard")
    
    
class PreferredLanguageChoices(models.TextChoices):
    FRENCH_CA   = "fr_CA", "Français (Canada)"   # type: ignore
    FRENCH_FR   = "fr_FR", "Français (France)"   # type: ignore
    ENGLISH_CA  = "en_CA", "English (Canada)"    # type: ignore
    ENGLISH_US  = "en_US", "English (US)"        # type: ignore