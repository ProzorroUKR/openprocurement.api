from schematics.types import MD5Type

from openprocurement.api.procedure.models.base import Model


class AgreementUUID(Model):
    id = MD5Type(required=True)
