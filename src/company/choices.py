from django.db import models
from django.utils.translation import gettext_lazy as _

class TranslationOptionChoices(models.TextChoices):
    DISABLED = "disabled", _("Disable data translation")
    GENERIC = "generic", _("Generic translations only")
    REGIONAL = "regional", _("Full translations (with regional variants)")

class UomTypeChoices(models.TextChoices):
    UNIT = "unit", _("Unit")
    WEIGHT = "weight", _("Weight")
    LENGTH = "length", _("Length")
    VOLUME = "volume", _("Volume")
    AREA = "area", _("Area")
    TIME = "time", _("Time")

class UomSystemChoices(models.TextChoices):
    IMPERIAL = "imperial", _("Imperial")
    METRIC = "metric", _("Metric")
    NONE = "none", _("None")

