from schematics.types import StringType

from openprocurement.api.procedure.models.base import Model


class Reference(Model):
    id = StringType(required=True)
    title = StringType()


class RequirementReference(Model):
    id = StringType(required=True)
