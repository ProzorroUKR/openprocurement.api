from schematics.types import StringType
from openprocurement.api.models import ContactPoint as BaseContactPoint


class ContactPoint(BaseContactPoint):
    availableLanguage = StringType(
        required=True,
        choices=['uk', 'en', 'ru'],default='uk'
    )