from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def home_view(request):
    """Vue temporaire pour afficher la page d'accueil du tableau de bord."""
    return render(request, "core/main.html")