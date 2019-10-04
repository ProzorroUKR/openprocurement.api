from openprocurement.api.models import ContactPoint as BaseContactPoint
from openprocurement.api.roles import RolesFromCsv
from schematics.types import StringType


class ContactPoint(BaseContactPoint):
    class Options:
        roles = RolesFromCsv("ContactPoint.csv", relative_to=__file__)

    name_en = StringType(required=True, min_length=1)
    availableLanguage = StringType(required=True, choices=["uk", "en", "ru"], default="uk")
