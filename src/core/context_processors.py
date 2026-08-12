from django.conf import settings

def project_context(request):
    """Injecte des variables globales dans l'ensemble des gabarits HTML."""
    return {
        "PROJECT_AUTHOR": getattr(settings, "PROJECT_AUTHOR", ""),
        "PROJECT_VERSION": getattr(settings, "PROJECT_VERSION", ""),
        "VISIBLE_LANGUAGES": getattr(settings, "VISIBLE_LANGUAGES", ""),
    }