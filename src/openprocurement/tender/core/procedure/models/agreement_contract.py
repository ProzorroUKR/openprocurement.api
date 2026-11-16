from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import (
    MD5,
)


class Contract(Model):
    id: MD5
