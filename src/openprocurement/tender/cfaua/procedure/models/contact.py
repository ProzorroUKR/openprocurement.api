from schematics.types import StringType

from openprocurement.tender.core.procedure.models.contact import (
    ContactPoint as BaseContactPoint,
)


class ContactPoint(BaseContactPoint):
    name_en = StringType(required=True, min_length=1)
    availableLanguage = StringType(required=True, choices=["uk", "en", "ru"], default="uk")
