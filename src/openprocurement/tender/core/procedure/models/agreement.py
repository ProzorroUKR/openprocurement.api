from openprocurement.api.models import Model
from schematics.types import MD5Type


class AgreementUUID(Model):
    id = MD5Type(required=True)
