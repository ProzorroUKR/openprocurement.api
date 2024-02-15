from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types import MD5Type, StringType

from openprocurement.api.constants import REQUESTED_REMEDIES_TYPES
from openprocurement.api.procedure.models.base import Model


class RequestedRemedy(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    type = StringType(required=True)
    description = StringType(required=True)

    def validate_type(self, data, value):
        if value not in REQUESTED_REMEDIES_TYPES:
            raise ValidationError(f"Value must be one of {REQUESTED_REMEDIES_TYPES}")
