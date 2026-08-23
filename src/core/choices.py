from django.db import models
from django.utils.translation import gettext_lazy as _

class ActionChoices(models.TextChoices):
    CREATE = 'CREATE', _('Create')
    UPDATE = 'UPDATE', _('Update')
    DELETE = 'DELETE', _('Delete')