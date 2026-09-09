
import contextvars
from typing import Optional

# Stocke l'ID de la compagnie active (un entier ou un UUID) ou None
_current_company_id: contextvars.ContextVar[Optional[int]] = contextvars.ContextVar(
    "current_company_id", default=None
)

# Permet de contourner les Manager personnalisés si on est dans l'admin django
_is_admin_route: contextvars.ContextVar[bool] = contextvars.ContextVar(
    "is_admin_route", default=False
)

class CompanyContext:
    """Stocke l'ID de la compagnie active et le mode admin django qui permet de désactiver les managers personnalisés"""

    @classmethod
    def set(cls, company_id: Optional[int]) -> contextvars.Token:
        """Fixe l'ID de l'entreprise pour la requête courante."""
        return _current_company_id.set(company_id)

    @classmethod
    def get(cls) -> Optional[int]:
        """Récupère l'ID de l'entreprise courante."""
        return _current_company_id.get()

    @classmethod
    def set_admin_mode(cls, is_admin: bool) -> contextvars.Token:
        """Indique si la requête est pour l'admin Django."""
        return _is_admin_route.set(is_admin)

    @classmethod
    def is_admin(cls) -> bool:
        """Retourne True si on est en mode admin."""
        return _is_admin_route.get()

    @classmethod
    def reset(cls, token: contextvars.Token) -> None:
        """Réinitialise le contexte à son état précédent (utile pour les tâches de fond)."""
        token.var.reset(token)

    @classmethod
    def clear(cls) -> None:
        """Vide explicitement le contexte actuel."""
        _current_company_id.set(None)
        _is_admin_route.set(False)