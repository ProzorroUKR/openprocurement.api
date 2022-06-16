from openprocurement.tender.core.procedure.models.identifier import Identifier as BaseIdentifier
from schematics.types import StringType, URLType, BaseType


class Identifier(BaseIdentifier):
    legalName_en = StringType(required=True, min_length=1)

