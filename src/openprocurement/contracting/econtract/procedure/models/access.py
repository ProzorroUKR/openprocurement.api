from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.identifier import Identifier
from openprocurement.api.procedure.types import ModelType


class PostAccess(Model):
    identifier = ModelType(Identifier, required=True)
