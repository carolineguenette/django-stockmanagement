from django.shortcuts import render

def register_view(request):
    """Vue publique temporaire pour le design de la page d'inscription."""
    return render(request, "users/register.html")

def password_reset_view(request):
    """Vue publique temporaire pour le design de la réinitialisation de mot de passe."""
    return render(request, "users/password_reset.html")