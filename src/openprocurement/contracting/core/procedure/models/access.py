from schematics.types import BooleanType, StringType
from schematics.types.serializable import serializable

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.identifier import Identifier
from openprocurement.api.procedure.types import ModelType


class PostAccess(Model):
    identifier = ModelType(Identifier, required=True)

    @serializable
    def active(self):
        return False


class PatchAccess(Model):
    identifier = ModelType(Identifier, required=True)
    active = BooleanType(choices=[True], required=True)


class AccessDetails(Model):
    owner = StringType()
    token = StringType()


class AccessRoles(Model):
    supplier = ModelType(AccessDetails)
    buyer = ModelType(AccessDetails)
