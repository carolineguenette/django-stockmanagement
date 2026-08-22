import threading
from django.conf import settings
from django.utils import translation
from django.utils.translation import get_language_from_request


_local = threading.local()

def get_current_user():
    """Permet de récupérer l'utilisateur connecté n'importe où dans le thread actuel."""
    return getattr(_local, 'user', None)

class AuditUserMiddleware:
    """
    Middleware pour capturer l'utilisateur de la requête HTTP.
    Utilisé par core.AbstractAudit et users.User lors du save pour définir les champs created_by et updated_by.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _local.user = request.user
        response = self.get_response(request)
        # Nettoyage après la requête
        if hasattr(_local, 'user'):
            del _local.user
        return response


class RegionalLocaleMiddleware:
    """
    Middleware gérant la localisation régionale (fr-ca, en-ca) sans préfixe d'URL.
    Utilise LANGUAGES_REGIONAL et LANGUAGES_FALLBACKS de settings.py.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Django a détecté la langue de base (via session, cookie ou navigateur)
        current_lang = translation.get_language()

        # Détermination de la famille (ex: 'fr' si on a 'fr-ca' ou juste 'fr')
        if current_lang:
            base_lang = current_lang.split("-")[0]
        else:
            base_lang = settings.LANGUAGE_CODE.split("-")[0]

        # Gestion pour l'utilisateur connecté (avec session)
        if request.user.is_authenticated:
            session_lang = request.session.get('django_language')

            # Si l'utilisateur navigue (session déjà settée), on respecte son choix
            # Si le choix en session correspond à la famille demandée (ex: clic sélecteur)
            if session_lang and session_lang.startswith(base_lang):
                target_lang = session_lang
            else:
                # Premier accès : on lit la préférence utilisateur en DB
                user_preference = getattr(request.user, "preferred_language", None)
                if user_preference and user_preference.lower().startswith(base_lang):
                    target_lang = user_preference.lower()
                else:
                    target_lang = self._resolve_regional_fallback(request, base_lang)

                # On fige le choix en session pour éviter de relire la DB
                request.session['django_language'] = target_lang

        # Gestion pour les utilisateurs anonymes
        else:
            target_lang = self._resolve_regional_fallback(request, base_lang)

        # Activation finale avec régionale
        translation.activate(target_lang)
        request.LANGUAGE_CODE = translation.get_language()

        try:
            return self.get_response(request)
        finally:
            translation.deactivate()

    def _resolve_regional_fallback(self, request, base_lang):
        """Détermine la version régionale via les réglages du settings.py."""
        browser_lang = get_language_from_request(request, check_path=False)

        # Récupération des config depuis settings
        supported_variants = getattr(settings, "LANGUAGES_REGIONAL", [])
        fallbacks = getattr(settings, "LANGUAGES_FALLBACKS", {})

        # Si le navigateur propose une variante supportée (ex: fr-fr)
        if browser_lang in supported_variants:
            return browser_lang

        # Sinon, règle de repli (ex: fr -> fr-ca) ou base_lang par défaut
        return fallbacks.get(base_lang, base_lang)
