from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types import MD5Type, StringType
from schematics.types.compound import ListType, ModelType

from openprocurement.api.context import get_request
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.validation import validate_items_uniq
from openprocurement.tender.core.procedure.context import get_complaint


class Evidence(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    title = StringType(required=True)
    description = StringType(serialize_when_none=True)
    relatedDocument = StringType(required=True)

    def validate_relatedDocument(self, data, value):
        complaint = get_complaint() or get_request().validated.get("json_data")
        if not complaint or value not in [document["id"] for document in complaint.get("documents", [])]:
            raise ValidationError("relatedDocument should be one of complaint documents")


class Argument(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    description = StringType(required=True)
    evidences = ListType(
        ModelType(Evidence),
        serialize_when_none=True,
        default=list(),
        validators=[
            validate_items_uniq,
        ],
    )
