from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from treebeard.mp_tree import MP_Node

from src.core.models import AbstractAudit


class UserHierarchy(MP_Node, AbstractAudit):
    """
    Relations hiérarchiques entre utilisateurs
    Un utilisateur peut avoir plusieurs relations hiérarchiques (apparaître dans différents arbres)
    """
    node_order_by = ["user"]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="hierarchy_nodes",
        verbose_name= _("User")
    )

    # MP_Node fournit automatiquement: path, depth, numchild

    class Meta:
        verbose_name = _("Hierarchy")
        verbose_name_plural = _("Hierarchies")

    def __str__(self):
        return f"{self.user} (depth: {self.depth})"