from schematics.types import StringType

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import URLType


class Project(Model):
    id = StringType()
    title = StringType(required=True)
    uri = URLType(required=True)
