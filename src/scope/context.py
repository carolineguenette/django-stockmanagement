
import contextvars
from typing import Optional

# Stocke l'ID de la compagnie active (un entier ou un UUID) ou None
_current_company_id: contextvars.ContextVar[Optional[int]] = contextvars.ContextVar(
    "current_company_id", default=None
)

class CompanyContext:
    """Stocke l'ID de la compagnie active"""

    @classmethod
    def set(cls, company_id: Optional[int]) -> contextvars.Token:
        """Fixe l'ID de l'entreprise pour la requête courante."""
        return _current_company_id.set(company_id)

    @classmethod
    def get(cls) -> Optional[int]:
        """Récupère l'ID de l'entreprise courante."""
        return _current_company_id.get()

    @classmethod
    def reset(cls, token: contextvars.Token) -> None:
        """Réinitialise le contexte à son état précédent (utile pour les tâches de fond)."""
        _current_company_id.reset(token)

    @classmethod
    def clear(cls) -> None:
        """Vide explicitement le contexte actuel."""
        _current_company_id.set(None)