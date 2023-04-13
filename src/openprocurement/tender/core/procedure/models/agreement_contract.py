from openprocurement.api.models import Model
from schematics.types import MD5Type


class Contract(Model):
    id = MD5Type(required=True)
