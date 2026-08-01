from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

# L'espace de noms isole ces URLs sous le préfixe 'users:'
app_name = "users"

urlpatterns = [
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="users/login.html"),
        name="login"
    ),
    path("register/", views.register_view, name="register"),
    path("password-reset/", views.password_reset_view, name="password_reset"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]