from django.db import models
from django.utils.translation import gettext_lazy as _

class TransitStatusChoices(models.TextChoices):
    PENDING = 'PENDING', _('Pending')
    CANCELLED_BY_SENDER = 'CANCELLED_BY_SENDER', _('Cancelled by sender')
    IN_TRANSIT = 'IN_TRANSIT', _('In Transit')
    DELIVERED = 'DELIVERED', _('Delivered')
    REFUSED_BY_RECIPIENT = 'REFUSED_BY_RECIPIENT', _('Refused by recipient')
    NEVER_RECEIVED = 'NEVER_RECEIVED', _('Never received')
    OTHER = 'OTHER', _('Other')
