from openprocurement.api.roles import RolesFromCsv
from schematics.types import StringType
from openprocurement.api.models import ContactPoint as BaseContactPoint


class ContactPoint(BaseContactPoint):
    class Options:
        roles = RolesFromCsv('ContactPoint.csv', relative_to=__file__)

    availableLanguage = StringType(
        required=True,
        choices=['uk', 'en', 'ru'],default='uk'
    )
