from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

from src.users.choices import PreferredHomePageChoices


class HomeView(LoginRequiredMixin, View):
    """
    Routeur central de la page d'accueil.
    Redirige dynamiquement l'utilisateur selon sa préférence de page d'accueil.
    """

    def get(self, request):
        user = request.user

        # Récupère la valeur en base de données
        db_preferred_home_page = getattr(user, 'preferred_home_page', PreferredHomePageChoices.DASHBOARD)

        try:
            # Conversion de la chaîne brute de la BD en notre objet énuméré
            page_choice = PreferredHomePageChoices(db_preferred_home_page)
            target_route = page_choice.route_name
        except ValueError:
            # Filet de sécurité au cas où la valeur en BD serait corrompue
            target_route = PreferredHomePageChoices.DASHBOARD.route_name

        # Redirection vers la route technique
        return redirect(target_route)
