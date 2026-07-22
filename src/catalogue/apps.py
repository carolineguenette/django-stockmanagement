from django.apps import AppConfig

class CatalogueConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.catalogue'

    def ready(self):
        # Listeners de nettoyage de fichiers d'images des produits
        import src.catalogue.signals
