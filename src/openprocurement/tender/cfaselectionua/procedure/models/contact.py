from openprocurement.tender.core.procedure.models.contact import ContactPoint as BaseContactPoint
from schematics.types import StringType


class ContactPoint(BaseContactPoint):
    availableLanguage = StringType(required=True, choices=["uk", "en", "ru"], default="uk")

