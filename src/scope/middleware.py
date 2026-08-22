import re

from django.http import Http404
from django.utils.translation import gettext_lazy as _
from src.company.models.company import Company
from src.scope.context import CompanyContext


class CompanyContextMiddleware:
    """Inspecte l'URL à l'arrivée d'une requête, vérifie en DB si la compagnie
     existe et récupère son ID si oui, met à jour le context avec l'ID de la
     compagnie active puis nettoie tout à la fin de la requête"""

    def __init__(self, get_response):
        self.get_response = get_response
        # Expression régulière pour détecter "/c/[slug]/" au début de l'URL
        self.company_url_pattern = re.compile(
            r"^/c/(?P<company_slug>[a-zA-Z0-9_-]+)(/|$)"
        )

    def __call__(self, request):
        path = request.path_info
        match = self.company_url_pattern.match(path)

        token = None
        if match:
            # L'URL commence par /c/<company-slug>
            company_slug = match.group("company_slug")
            try:
                # Récupérer l'ID de l'entreprise à partir du slug
                company_id = (
                    Company.objects.filter(slug=company_slug)
                    .values_list("id", flat=True)
                    .get()
                )
                token = CompanyContext.set(company_id)
                request.current_company_id = company_id
            except Company.DoesNotExist:
                raise Http404(_("Company not found."))
        else:
            # L'URL n'est pas lié à une entreprise active unique
            #   (pas de /c/<company-slug> trouvé)
            token = CompanyContext.set(None)
            request.current_company_id = None

        try:
            response = self.get_response(request)
            return response
        finally:
            if token:
                CompanyContext.reset(token)
            else:
                CompanyContext.clear()
