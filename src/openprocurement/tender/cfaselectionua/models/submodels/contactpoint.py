from openprocurement.api.models import ContactPoint as BaseContactPoint
from openprocurement.api.roles import RolesFromCsv
from schematics.types import StringType


class ContactPoint(BaseContactPoint):
    class Options:
        roles = RolesFromCsv('ContactPoint.csv', relative_to=__file__)
    availableLanguage = StringType(choices=['uk', 'en', 'ru'])
