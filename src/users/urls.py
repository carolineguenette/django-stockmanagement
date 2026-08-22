from django.urls import path
from django.contrib.auth import views as django_auth_views
from src.users.views.auth_views import PasswordResetView, RegisterView

# L'espace de noms isole ces URLs sous le préfixe 'users:'
app_name = "users"

urlpatterns = [
    path(
        "login/",
        django_auth_views.LoginView.as_view(template_name="users/login.html"),
        name="login"
    ),
    path("register/", RegisterView.as_view(), name="register"),
    path("password-reset/", PasswordResetView.as_view(), name="password_reset"),
    path("logout/", django_auth_views.LogoutView.as_view(), name="logout"),
]
