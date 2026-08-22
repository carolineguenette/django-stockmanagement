import pytest
import warnings
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory

from src.access.choices import PermissionContextChoices as Ctx
from src.access.auth_backend import CompanyRBACBackend
from src.access.models.permission import Permission
from src.access.models.role import Role
from src.access.models.role_permissions import RolePermission
from src.users.models.user_role import UserRole
from src.company.models.company import Company

User = get_user_model()


@pytest.fixture
def backend() -> CompanyRBACBackend:
    """Fixture pour instancier le backend de permission RBAC."""
    return CompanyRBACBackend()


@pytest.fixture
def factory() -> RequestFactory:
    """Fixture pour générer de fausses requêtes HTTP."""
    return RequestFactory()


@pytest.fixture
def company_a(db) -> Company:
    """Crée une entreprise A pour les tests de contexte."""
    return Company.objects.create(official_name="Company A Inc.", slug="company-a")


@pytest.fixture
def company_b(db) -> Company:
    """Crée une deuxième entreprise B pour les tests multi-entreprises."""
    return Company.objects.create(official_name="Company B Inc.", slug="company-b")


@pytest.fixture
def perm_system(db) -> Permission:
    """Crée une permission globale de type SYSTEM."""
    return Permission.objects.create(
        name="System Backup",
        codename="system.backup",
        context=Ctx.SYSTEM,
        is_active=True,
    )


@pytest.fixture
def perm_company(db) -> Permission:
    """Crée une permission liée à une entreprise."""
    return Permission.objects.create(
        name="View Dashboard",
        codename="company.dashboard.view",
        context=Ctx.COMPANY,
        is_active=True,
    )


@pytest.fixture
def perm_delegate(db) -> Permission:
    """Crée une permission de délégation (ex: Gestion des rôles)."""
    return Permission.objects.create(
        name="Manage Roles",
        codename="access.role.manage",
        context=Ctx.DELEGATE,
        is_active=True,
    )


@pytest.mark.django_db(transaction=True)
class TestCompanyRBACBackendValidation:
    """Focalisé sur la validation du paramètre 'obj' et des structures de données."""

    def test_has_perm_inactive_user_returns_false(
        self, backend: CompanyRBACBackend, perm_system: Permission
    ):
        """Un utilisateur inactif doit immédiatement recevoir False."""
        user = User.objects.create_user(
            username="inactive", password="123", is_active=False
        )
        assert backend.has_perm(user, perm_system.codename) is False

    def test_has_perm_owner_bypass_returns_true(
        self, backend: CompanyRBACBackend, perm_system: Permission
    ):
        """Un utilisateur marqué 'is_owner' passe outre toutes les vérifications."""
        user = User.objects.create_user(
            username="owner", password="123", is_active=True
        )
        user.is_owner = True  # Simulation du flag propriétaire
        assert backend.has_perm(user, perm_system.codename) is True

    def test_missing_dict_context_raises_permission_denied(
        self, backend: CompanyRBACBackend, perm_company: Permission
    ):
        """Si le contexte réclame un dictionnaire et qu'on passe None, lever une exception."""
        user = User.objects.create_user(username="user", password="123", is_active=True)
        with pytest.raises(PermissionDenied) as exc_info:
            backend.has_perm(user, perm_company.codename, obj=None)
        assert "A context dictionary (obj) is required" in str(exc_info.value)

    def test_system_context_with_obj_triggers_warning(
        self, backend: CompanyRBACBackend, perm_system: Permission
    ):
        """Le contexte SYSTEM n'a pas besoin d'objet. Si fourni, émettre un avertissement."""
        user = User.objects.create_user(username="user", password="123", is_active=True)
        context_inutile = {"company_id": 1}

        with pytest.warns(UserWarning) as record:
            backend.has_perm(user, perm_system.codename, obj=context_inutile)

        assert len(record) == 1
        assert "ignores the provided context" in str(record[0].message)


@pytest.mark.django_db(transaction=True)
class TestRBACCoreLogicAndDelegation:
    """Focalisé sur l'évaluation SQL en base de données et la règle de Suzie (RH)."""

    def test_inactive_role_is_ignored(
        self, backend: CompanyRBACBackend, perm_company: Permission, company_a: Company
    ):
        """Si un rôle est inactif, l'utilisateur ne doit pas obtenir la permission."""
        user = User.objects.create_user(
            username="testuser", password="123", is_active=True
        )

        # Création d'un rôle inactif contenant la bonne permission
        role_inactif = Role.objects.create(
            name="Inactif", company=company_a, is_active=False
        )
        RolePermission.objects.create(role=role_inactif, permission=perm_company)
        UserRole.objects.create(user=user, role=role_inactif, is_active=True)

        context = {"company_id": company_a.id}
        assert backend.has_perm(user, perm_company.codename, obj=context) is False

    def test_delegate_dont_give_perm_for_permission_in_same_role(
        self,
        backend: CompanyRBACBackend,
        perm_company: Permission,
        perm_delegate: Permission,
        company_a: Company,
    ):
        """
        Règle :
        Un rôle possédant une permission DELEGATE ne doit JAMAIS donner accès
        aux permissions associées sur le même rôle car ces permissions représentent
        les permissions déléguées à l'utilisateur et non pas un accès métier.
        """
        suzie = User.objects.create_user(
            username="suzie", password="123", is_active=True
        )

        # 1. On crée le rôle RH de Suzie lié à l'entreprise A
        role_rh = Role.objects.create(
            name="Ressources Humaines", company=company_a, is_active=True
        )

        # 2. Ce rôle possède la délégation ET l'action opérationnelle (ex: modifier les stocks / voir dashboard)
        RolePermission.objects.create(
            role=role_rh, permission=perm_delegate
        )  # TYPE: DELEGATE
        RolePermission.objects.create(
            role=role_rh, permission=perm_company
        )  # TYPE: COMPANY

        # 3. On affecte ce rôle à Suzie
        UserRole.objects.create(user=suzie, role=role_rh, is_active=True)

        context = {"company_id": company_a.id}

        # TEST A : Suzie demande à gérer les rôles (DELEGATE) -> Doit fonctionner (True)
        assert backend.has_perm(suzie, perm_delegate.codename, obj=context) is True

        # TEST B : Suzie tente d'utiliser ce même rôle pour voir le Dashboard (COMPANY) -> Doit être bloquée (False)
        # La sous-requête SQL ~Exists doit détecter la présence de perm_delegate et invalider le rôle RH.
        assert backend.has_perm(suzie, perm_company.codename, obj=context) is False

    def test_user_with_delegate_and_normal_perms_has_normal_perm_access(
        self,
        backend: CompanyRBACBackend,
        perm_company: Permission,
        perm_delegate: Permission,
        company_a: Company,
    ):
        """
        Si Suzie possède DEUX rôles distincts : un rôle RH (DELEGATE) et un rôle Employé (COMPANY),
        le rôle Employé doit lui permettre d'exécuter l'action COMPANY normalement.
        """
        suzie = User.objects.create_user(
            username="suzie_double", password="123", is_active=True
        )

        # Rôle 1 : RH (Délégation uniquement)
        role_rh = Role.objects.create(slug="rh-pur", name="RH Pur", company=company_a, is_active=True)
        RolePermission.objects.create(role=role_rh, permission=perm_delegate)
        UserRole.objects.create(user=suzie, role=role_rh, is_active=True)

        # Rôle 2 : Employé (Opérationnel uniquement)
        role_employe = Role.objects.create(
            slug="employe", name="Employé", company=company_a, is_active=True
        )
        RolePermission.objects.create(role=role_employe, permission=perm_company)
        UserRole.objects.create(user=suzie, role=role_employe, is_active=True)

        context = {"company_id": company_a.id}

        # Le rôle Employé n'ayant aucune permission DELEGATE, il n'est pas exclu par le backend !
        assert backend.has_perm(suzie, perm_company.codename, obj=context) is True
