from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types import MD5Type
from schematics.types import StringType
from schematics.types.compound import ModelType

from openprocurement.api.models import Model
from openprocurement.api.models import Reference
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.core.procedure.utils import bid_in_invalid_status


class BaseEligibleEvidence(Model):
    title = StringType()
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    type = StringType(
        choices=["document", "statement"],
        default="statement"
    )
    relatedDocument = ModelType(Reference)


class EligibleEvidence(BaseEligibleEvidence):
    id = MD5Type(required=True, default=lambda: uuid4().hex)

    def validate_relatedDocument(self, data, document_reference):
        if document_reference:
            tender = get_tender()
            if not any(d and document_reference.id == d["id"] for d in tender.get("documents")):
                raise ValidationError("relatedDocument.id should be one of tender documents")


class PatchEvidence(BaseEligibleEvidence):
    type = StringType(choices=["document", "statement"])


class Evidence(EligibleEvidence):

    def validate_relatedDocument(self, data, document_reference):
        if bid_in_invalid_status():
            return

        if data["type"] in ["document"] and not document_reference:
            raise ValidationError("This field is required.")
