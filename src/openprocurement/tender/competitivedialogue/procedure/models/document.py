from openprocurement.api.procedure.models.base import model_field_validator
from openprocurement.api.procedure.models.document import validate_confidentiality_rationale
from openprocurement.tender.core.procedure.models.document import Document, PatchDocument, PostDocument


class CDBidPostDocument(PostDocument):
    isDescriptionDecision: bool = False

    @model_field_validator("confidentialityRationale")
    def validate_confidentiality_rationale(self, val):
        if not self.isDescriptionDecision:
            validate_confidentiality_rationale(self.confidentiality, val)


class CDBidPatchDocument(PatchDocument):
    isDescriptionDecision: bool | None = None


class CDBidDocument(Document):
    isDescriptionDecision: bool | None = None

    @model_field_validator("confidentialityRationale")
    def validate_confidentiality_rationale(self, val):
        if not self.isDescriptionDecision:
            validate_confidentiality_rationale(self.confidentiality, val)
