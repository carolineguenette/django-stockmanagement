# src/core/views/debug_views.py
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from src.users.choices import PreferredHomePageChoices

class HomeDebugView(LoginRequiredMixin, View):
    """
    Vue de diagnostic qui transmet les métadonnées de l'infrastructure
    au gabarit HTML pour affichage dans le cadre de l'application.
    """
    def get(self, request):
        user = request.user
        db_preferred_home_page = getattr(user, 'preferred_home_page', None)
        db_preferred_language = getattr(user, 'preferred_language', None)

        try:
            page_choice = PreferredHomePageChoices(db_preferred_home_page)
            calculated_route = page_choice.route_name
            status_message = "✅ Préférence utilisateur valide"
        except ValueError:
            calculated_route = PreferredHomePageChoices.DASHBOARD.route_name
            status_message = "⚠️ Valeur inconnue en BD, repli par défaut"

        # On prépare les variables pour le template HTML
        context = {
            "debug_username": user.username,
            "debug_user_id": user.id,
            "debug_is_owner": getattr(user, "is_owner", False),
            "debug_db_language": db_preferred_language,
            "debug_request_language": request.LANGUAGE_CODE,
            "debug_db_home_page": db_preferred_home_page,
            "debug_status_message": status_message,
            "debug_target_route": calculated_route,
        }

        return render(request, "core/home_debug.html", context)