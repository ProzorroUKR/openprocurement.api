from schematics.types import BaseType, StringType

from openprocurement.api.constants import ORA_CODES
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import URLType


class Identifier(Model):
    scheme = StringType(choices=ORA_CODES, required=True)
    id = BaseType(required=True)
    legalName = StringType()
    legalName_en = StringType()
    legalName_ru = StringType()
    uri = URLType()
