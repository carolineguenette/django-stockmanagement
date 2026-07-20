# src/catalogue/urls.py
from django.urls import path
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _

# Fonction de vue temporaire et traduisible pour le catalogue
def catalogue_placeholder_view(request):
    return HttpResponse(f"<h1>{_('Product Catalog')}</h1>")

app_name = 'catalogue'

urlpatterns = [
    path('products/', catalogue_placeholder_view, name='product_list'),
]
