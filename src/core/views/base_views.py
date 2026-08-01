from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View


class HomeView(LoginRequiredMixin, View):

    # TODO Pour une future fonctionnalité où l'utilisateur peut choisir sa page d'accueil préférée.
    HOMEPAGE_ROUTES = {
        "inventory": "catalogue:product_list",
        "scanner": "inventory:barcode_scanner",
        "dashboard": "reporting:dashboard",
    }

    """
    Routeur central de la page d'accueil.
    Redirige dynamiquement l'utilisateur selon ses préférences.
    """
    def get(self, request):
        user = request.user

        # Récupère la préférence de l'utilisateur si le champ existe
        preferred_page = getattr(user, 'preferred_home_page', None)

        # Cherche la route correspondante
        target_route = self.HOMEPAGE_ROUTES.get(preferred_page)

        if target_route:
            return redirect(target_route)

        return render(request, "core/main.html")
