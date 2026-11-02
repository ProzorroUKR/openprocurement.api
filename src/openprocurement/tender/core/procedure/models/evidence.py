from uuid import uuid4

from schematics.types import MD5Type, StringType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.reference import Reference


class BaseEligibleEvidence(Model):
    title = StringType()
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    type = StringType(choices=["document", "statement"], default="statement")
    relatedDocument = ModelType(Reference)


class EligibleEvidence(BaseEligibleEvidence):
    id = MD5Type(required=True, default=lambda: uuid4().hex)


class PatchEvidence(BaseEligibleEvidence):
    type = StringType(choices=["document", "statement"])


class Evidence(EligibleEvidence):
    # relatedDocument is required for the document type by the state (validate_evidence_related_document)
    pass
