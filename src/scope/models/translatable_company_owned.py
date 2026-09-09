from parler.models import TranslatableModel

from src.scope.models.company_owned import CompanyOwned
from src.scope.managers.company_managers import CompanyScopedTranslatableManager
from src.scope.managers.companies_managers import CompaniesScopedTranslatableManager
from src.scope.managers.unscoped_managers import UnscopedTranslatableManager

class TranslatableCompanyOwned(TranslatableModel, CompanyOwned):
    objects = CompanyScopedTranslatableManager()
    companies = CompaniesScopedTranslatableManager()
    unscoped = UnscopedTranslatableManager()

    class Meta:
        abstract = True