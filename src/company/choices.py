from django.db import models
from django.utils.translation import gettext_lazy as _

class TranslationModeChoices(models.TextChoices):
    DISABLED = "DISABLED", _("Disable data translation")
    GENERIC = "LANGUAGE", _("Generic translations (en, fr, etc)")
    REGIONAL = "REGIONAL", _("Full translations (with regional variants)")

class UomTypeChoices(models.TextChoices):
    UNIT = "UNIT", _("Unit")
    WEIGHT = "WEIGHT", _("Weight")
    LENGTH = "LENGTH", _("Length")
    VOLUME = "VOLUME", _("Volume")
    AREA = "AREA", _("Area")
    TIME = "TIME", _("Time")

class UomSystemChoices(models.TextChoices):
    NONE = "NONE", _("None")
    METRIC = "METRIC", _("Metric")
    IMPERIAL = "IMPERIAL", _("Imperial")

