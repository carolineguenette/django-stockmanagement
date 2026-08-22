from django.db import models
from django.utils.translation import gettext_lazy as _

class PreferredHomePageChoices(models.TextChoices):
    # Format : CONSTANT_NAME = "valeur_bd", _("Translate Label")
    DASHBOARD = "dashboard", _("Dashboard")         # type: ignore - car linter ne gère pas le _() de type StrPromise (avertissement)
    INVENTORY = "inventory", _("Inventory")
    SCANNER   = "scanner", _("Barcode scanner")
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
        # Retourne la route associée
        return mapping.get(self, "404")
    
    
class PreferredLanguageChoices(models.TextChoices):
    DEFAULT    = "default", _("Default")  # As Navigator language request
    ENGLISH    = "en"   , "English"
    ENGLISH_CA = "en-ca", "English (Canada)"
    ENGLISH_US = "en-us", "English (US)"
    FRENCH     = "fr"   , "Français"
    FRENCH_CA  = "fr-ca", "Français (Canada)"
    FRENCH_FR  = "fr-fr", "Français (France)"
