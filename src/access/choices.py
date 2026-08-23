from django.db import models
from django.utils.translation import gettext_lazy as _

class PermissionContextChoices(models.TextChoices):
    SYSTEM = 'SYSTEM', _('System')
    DELEGATE = 'DELEGATE', _('Delegate')
    COMPANY = 'COMPANY', _('Company')
    MULTI_COMPANIES = 'MULTI_COMPANIES', _('Multi-companies')
    LOCATION = 'LOCATION', _('Location')
    MULTI_LOCATIONS = 'MULTI_LOCATIONS', _('Multi-locations')

class PermissionSensibilityChoices(models.TextChoices):
    HIGH = 'HIGH', _('High')
    MEDIUM = 'MEDIUM', _('Medium')
    LOW = 'LOW', _('Low')

class AccessLogTargetChoices(models.TextChoices):
    ACCESS_PERMISSION = "access_permission", _("Access permission")
    ACCESS_ROLE = "access_role", _("Access role")