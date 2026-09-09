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
        # Expression régulière pour détecter "/admin/" au début de l'URL
        self.admin_url_pattern = re.compile(r"^/admin/")


    def __call__(self, request):
        path = request.path_info

        # Détecter si on est dans l'admin
        is_admin = bool(self.admin_url_pattern.match(path))
        admin_token = CompanyContext.set_admin_mode(is_admin)

        company_token = None
        if not is_admin:
            match = self.company_url_pattern.match(path)
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
                    company_token = CompanyContext.set(company_id)
                    request.current_company_id = company_id
                except Company.DoesNotExist:
                    raise Http404(_("Company not found."))
            else:
                # L'URL n'est pas lié à une entreprise active unique
                #   (pas de /c/<company-slug> trouvé)
                company_token = CompanyContext.set(None)
                request.current_company_id = None
        else:
            # Admin : pas de contexte de compagnie
            request.current_company_id = None

        try:
            response = self.get_response(request)
            return response
        finally:
            CompanyContext.reset(admin_token)
            if company_token:
                CompanyContext.reset(company_token)
            else:
                CompanyContext.clear()
