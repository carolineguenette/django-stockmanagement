from django.views.generic import TemplateView

# TemplateView (une vue générique de Django) fait qu'on n'a même pas besoin d'écrire la méthode get()
# car django sait qu'il doit simplement renvoyer le template_name

class RegisterView(TemplateView):
    """Vue publique temporaire pour le design de la page d'inscription."""
    template_name = "users/register.html"


class PasswordResetView(TemplateView):
    """Vue publique temporaire pour le design de la réinitialisation de mot de passe."""
    template_name = "users/password_reset.html"