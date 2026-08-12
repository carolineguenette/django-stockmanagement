import pytest
from src.company.models.company import Company
from src.scope.context import CompanyContext

@pytest.fixture
def company_apple(db):
    """Génère l'entreprise Apple en base pour la durée d'un test."""
    return Company.objects.create(official_name="Apple Inc", slug="apple")

@pytest.fixture
def company_google(db):
    """Génère l'entreprise Google en base pour la durée d'un test."""
    return Company.objects.create(official_name="Google LLC", slug="google")

@pytest.fixture
def activate_apple_context(company_apple):
    """Active automatiquement le contexte Apple et assure le nettoyage après le test."""
    token = CompanyContext.set(company_apple.id)
    yield company_apple
    CompanyContext.clear()