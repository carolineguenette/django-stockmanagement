import pytest
from src.catalogue.models.product import Product

@pytest.mark.django_db
def test_database_isolation_by_company(
        company_apple, company_google, activate_apple_context
):
    # 1. Le contexte Apple est DÉJÀ actif ici grâce à l'argument 'activate_apple_context'

    # 2. Création des produits
    prod_iphone = Product.objects.create(name="iPhone", company=company_apple)
    prod_pixel = Product.objects.create(name="Pixel", company=company_google)

    # 3. La requête globale ne retourne que l'iPhone, car le contexte Apple est actif
    products = Product.objects.all()
    assert products.count() == 1
    assert prod_iphone in products
    assert prod_pixel not in products

    # Le nettoyage du contexte se fera automatiquement à la sortie du test
    # grâce au 'yield' présent dans la fixture de conftest.py