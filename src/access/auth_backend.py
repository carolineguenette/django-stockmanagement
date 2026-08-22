# django-stock/src/access/auth_backends.py

import logging
import warnings
from typing import Any, Optional

from django.core.exceptions import PermissionDenied
from django.db.models import Q, OuterRef, Exists
from django.utils.translation import gettext_lazy as _

from src.access.choices import PermissionContextChoices as Ctx
from src.access.models.permission import Permission
from src.access.models.role_permissions import RolePermission
from src.users.models.user_role import UserRole
from src.company.models.location import Location

logger = logging.getLogger(__name__)

class CompanyRBACBackend:
    """
    Backend de permission personnalisé pour gérer le RBAC par Compagnie et Location.
    Optimisé pour minimiser les requêtes à la base de données
        - 1 requête (toujours)
        - 2ìème requête si un contexte de location doit être validé aussi
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # On laisse le backend par défaut (ModelBackend) gérer le login
        return None

    def has_perm(self, user_obj: Any, perm: str, obj: Optional[dict] = None) -> bool:
        """
        Surcharge la vérification des permissions de Django avec une version qui
        va interroger le RBAC Custom
        """
        # Sécurité de base sur l'utilisateur
        if not user_obj.is_active:
            return False

        # Bypass complet pour le Propriétaire (Owner)
        if getattr(user_obj, 'is_owner', False):
            return True

        # [REQUÊTE SQL 1] : Extraction du contexte de la permission demandée
        try:
            # On cherche par 'codename' (ex: 'catalogue.product.delete')
            permission = Permission.objects.get(codename=perm, is_active=True)
        except Permission.DoesNotExist:
            return False

        # Validation de la structure du dictionnaire `obj` selon le contexte de la permission
        self._validate_context_object(permission, obj)

        # Extraction des valeurs du dictionnaire validé
        company_id = obj.get('company_id') if isinstance(obj, dict) else None
        location_id = obj.get('location_id') if isinstance(obj, dict) else None

        # [REQUÊTE SQL 2] : Évaluation atomique de la matrice via l'ORM
        return self._evaluate_access_via_db(user_obj, permission, company_id, location_id)


    def _validate_context_object(self, permission, obj):
        """
        Validation de la structure du paramètre `obj` (Arbre de validation).
        Émet des avertissements ou lève une exception selon la validité.
        """
        ctx_type = permission.context
        codename = permission.codename
        perm_name = permission.name

        # Message d'erreur de base réutilisable pour structurer les exceptions
        # Permet aux traducteurs d'avoir un contexte clair dans les fichiers .po
        base_err = _(
            "Invalid context for permission '{perm_name}' ({codename}) [Context: {ctx_type}]: "
        ).format(perm_name=perm_name, codename=codename, ctx_type=ctx_type)

        # --- VALIDATION INITIALE : Est-ce un dictionnaire ? ---
        if ctx_type != Ctx.SYSTEM and not isinstance(obj, dict):
            raise PermissionDenied(
                base_err + _("A context dictionary (obj) is required.")
            )

        # Extraction sécurisée des valeurs
        company_id = obj.get('company_id') if obj else None
        location_id = obj.get('location_id') if obj else None

        # --- SYSTEM ---
        if ctx_type == Ctx.SYSTEM:
            if company_id is not None or location_id is not None:
                warnings.warn(
                    _(
                        "SYSTEM permission '{perm_name}' ({codename}) ignores the provided context."
                    ).format(perm_name=perm_name, codename=codename),
                    UserWarning
                )

        # --- DELEGATE ---
        elif ctx_type == Ctx.DELEGATE:
            if not company_id:
                raise PermissionDenied(base_err + _("Missing company context ('company_id')."))
            if isinstance(company_id, list):
                raise PermissionDenied(base_err + _("Too many companies provided (Array not supported)."))
            if location_id is not None:
                warnings.warn(
                    _(
                        "Location context provided for DELEGATE permission '{perm_name}' ({codename}) was ignored."
                    ).format(perm_name=perm_name, codename=codename),
                    UserWarning
                )

        # --- COMPANY ---
        elif ctx_type == Ctx.COMPANY:
            if not company_id:
                raise PermissionDenied(base_err + _("Missing company context ('company_id')."))
            if isinstance(company_id, list):
                raise PermissionDenied(base_err + _("Too many companies provided (Array not supported)."))
            if location_id is not None:
                warnings.warn(
                    _(
                        "Location context provided for COMPANY permission '{perm_name}' ({codename}) was ignored."
                    ).format(perm_name=perm_name, codename=codename),
                    UserWarning
                )

        # --- MULTI_COMPANIES ---
        elif ctx_type == Ctx.MULTI_COMPANIES:
            if not company_id:
                raise PermissionDenied(base_err + _("Missing company context ('company_id')."))
            if location_id is not None:
                warnings.warn(
                    _(
                        "Location context provided for MULTI_COMPANIES permission '{perm_name}' ({codename}) was ignored."
                    ).format(perm_name=perm_name, codename=codename),
                    UserWarning
                )

        # --- LOCATION ---
        elif ctx_type == Ctx.LOCATION:
            if not company_id or isinstance(company_id, list):
                raise PermissionDenied(base_err + _("A single company ('company_id') is required."))
            if not location_id or isinstance(location_id, list):
                raise PermissionDenied(base_err + _("A single location ('location_id') is required."))

        # --- MULTI_LOCATIONS ---
        elif ctx_type == Ctx.MULTI_LOCATIONS:
            if not company_id or isinstance(company_id, list):
                raise PermissionDenied(base_err + _("A single company ('company_id') is required."))
            if not location_id or not isinstance(location_id, list):
                raise PermissionDenied(base_err + _("An array of locations ('location_id') is required."))
            if len(location_id) < 2:
                raise PermissionDenied(base_err + _("At least 2 locations are required in the array."))


    def _evaluate_access_via_db(self, user_obj, permission, company_id, location_id):
        """
        Vérifie l'existence d'une assignation valide en base de données.
        Version corrigée et étanche pour la règle DELEGATE (Règle Suzie / RH).
        """
        ctx_type = permission.context
        requested_companies = (
            company_id if isinstance(company_id, list) else [company_id]
        )

        # 1. Filtre de base : l'affectation et le rôle doivent être actifs
        role_filters = Q(user=user_obj, is_active=True, role__is_active=True)

        # 2. RÈGLE DE DÉLÉGATION (Stricte et Étanche)
        if ctx_type == Ctx.DELEGATE:
            # Si on évalue une permission de type DELEGATE, l'utilisateur DOIT
            # utiliser un rôle explicitement configuré pour cette entreprise.
            role_filters &= Q(role__company_id__isnull=False)
        else:
            # Si on évalue n'importe quel AUTRE type de permission (COMPANY, LOCATION, SYSTEM...),
            # on doit s'assurer que le rôle utilisé ne possède AUCUNE permission de type DELEGATE.
            # Cela empêche Suzie d'utiliser son rôle RH pour exécuter des actions opérationnelles.
            roles_avec_delegation = RolePermission.objects.filter(
                role=OuterRef("role_id"), permission__context=Ctx.DELEGATE
            )
            role_filters &= ~Exists(roles_avec_delegation)

        # 3. Isolation des entreprises selon le contexte requis
        if ctx_type in [Ctx.COMPANY, Ctx.DELEGATE, Ctx.LOCATION, Ctx.MULTI_LOCATIONS]:
            role_filters &= Q(role__company_id=company_id)
        elif ctx_type == Ctx.MULTI_COMPANIES:
            role_filters &= Q(role__company_id__in=requested_companies)

        # 4. Association avec la permission spécifique recherchée
        role_filters &= Q(role__permissions=permission)

        # 5. Évaluation de la hiérarchie spatiale MP_Node (Treebeard)
        if ctx_type == Ctx.LOCATION:
            role_filters &= Q(location_id__isnull=False)
            role_filters &= Exists(
                Location.objects.filter(
                    id=location_id, path__startswith=OuterRef("location__path")
                )
            )

        elif ctx_type == Ctx.MULTI_LOCATIONS:
            role_filters &= Q(location_id__isnull=False)
            locations_valides = (
                Location.objects.filter(
                    id__in=location_id, path__startswith=OuterRef("location__path")
                )
                .values("id")
                .distinct()
            )
            role_filters &= Exists(locations_valides)

        # 6. Exécution de la requête d'existence atomique
        return UserRole.objects.filter(role_filters).exists()
