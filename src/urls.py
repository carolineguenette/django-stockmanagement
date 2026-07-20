"""
URL configuration for src project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.views.generic.base import RedirectView
from django.conf import settings
from django.shortcuts import render

# TODO Temporaire
def home_view(request):
    return render(request, 'main.html')


# Les URLs sans préfixe de langue (ex: API ou Webhooks)
urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'img/favicon.ico')), #TODO Temporaire
    path('i18n/', include('django.conf.urls.i18n')),
]

# Les URLs traduits et préfixés (ex: /fr/admin/, /en/catalogue/)
urlpatterns += i18n_patterns(
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('catalogue/', include('src.catalogue.urls')),

    prefix_default_language=False
)
