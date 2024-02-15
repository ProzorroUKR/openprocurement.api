from schematics.types import StringType

from openprocurement.api.procedure.models.identifier import Identifier as BaseIdentifier


class Identifier(BaseIdentifier):
    legalName_en = StringType(required=True, min_length=1)
