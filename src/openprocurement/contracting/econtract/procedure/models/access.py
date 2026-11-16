from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.identifier import Identifier


class PostAccess(Model):
    identifier: Identifier
