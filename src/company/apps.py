from django.apps import AppConfig

# Cette section gère les structures organisationnelles : les entreprises (Company), ses sites physiques de haut niveau (Location
# avec location_id = NULL et les définitions des localisations fines (location avec location_id != NULL).


class CompanyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "src.company"
