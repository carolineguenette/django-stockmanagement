from django.db import models
from django.utils.translation import gettext_lazy as _

class PermissionContextChoices(models.TextChoices):
    SYSTEM = 'SYSTEM', _('System')
    COMPANY = 'COMPANY', _('Company')
    MULTI_COMPANIES = 'MULTI_COMPANIES', _('Multi-companies')
    LOCATION = 'LOCATION', _('Location')
    MULTI_LOCATIONS = 'MULTI_LOCATIONS', _('Multi-locations')

class PermissionSensibilityChoices(models.TextChoices):
    HIGH = 'HIGH', _('High')
    MEDIUM = 'MEDIUM', _('Medium')
    LOW = 'LOW', _('Low')

class PermissionCategoryChoices(models.TextChoices):
    ACCESS = 'ACCESS', _('Access')
    DELEGATE = 'DELEGATE', _('Delegate')
    USERS = 'USERS', _('Users')
    COMPANY = 'COMPANY', _('Company')
    CATALOGUE = 'CATALOGUE', _('Catalogue')
    INVENTORY = 'INVENTORY', _('Inventory')
    MOVEMENT = 'MOVEMENT', _('Movement')
    REPORTING = 'REPORTING', _('Reporting')

class AccessLogTargetChoices(models.TextChoices):
    ACCESS_ROLE = "access_role", _("Role")
    ACCESS_PERMISSION = "access_rolepermissions", _("Permission")
    ACCESS_DELEGATE = "access_roledelegatepermissions", _("Delegate")
