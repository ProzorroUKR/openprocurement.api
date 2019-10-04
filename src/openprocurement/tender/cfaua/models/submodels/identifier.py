from openprocurement.api.models import Identifier as BaseIdentifier
from openprocurement.api.roles import RolesFromCsv
from schematics.types import StringType


class Identifier(BaseIdentifier):
    class Options:
        roles = RolesFromCsv("Identifier.csv", relative_to=__file__)

    legalName_en = StringType(required=True, min_length=1)
