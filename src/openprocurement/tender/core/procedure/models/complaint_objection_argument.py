from uuid import uuid4

from schematics.types import MD5Type, StringType
from schematics.types.compound import ListType, ModelType

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.validation import validate_uniq_id


class Evidence(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    title = StringType(required=True)
    description = StringType(serialize_when_none=True)
    relatedDocument = StringType(required=True)


class Argument(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    description = StringType(required=True)
    evidences = ListType(
        ModelType(Evidence, required=True),
        serialize_when_none=True,
        default=[],
        validators=[validate_uniq_id],
    )
