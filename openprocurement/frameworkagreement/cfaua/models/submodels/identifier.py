from openprocurement.api.models import Identifier as BaseIdentifier
from schematics.types import StringType


class Identifier(BaseIdentifier):
    legalName_en = StringType(required=True, min_length=1)