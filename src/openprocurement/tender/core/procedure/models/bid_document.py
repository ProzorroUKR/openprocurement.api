from schematics.types import StringType
from schematics.exceptions import ValidationError
from openprocurement.tender.core.procedure.models.document import (
    PostDocument as BasePostDocument,
    PatchDocument as BasePatchDocument,
    Document as BaseDocument,
)


def validate_confidentiality_rationale(data, val):
    confidentiality = data.get("confidentiality")
    if confidentiality == "buyerOnly":
        if not val:
            raise ValidationError("confidentialityRationale is required")
        elif len(val) < 30:
            raise ValidationError("confidentialityRationale should contain at least 30 characters")


class PostDocument(BasePostDocument):
    confidentiality = StringType(choices=["public", "buyerOnly"], default="public")
    confidentialityRationale = StringType()

    def validate_confidentialityRationale(self, data, val):
        validate_confidentiality_rationale(data, val)


class PatchDocument(BasePatchDocument):
    confidentiality = StringType(choices=["public", "buyerOnly"])
    confidentialityRationale = StringType()


class Document(BaseDocument):
    confidentiality = StringType(choices=["public", "buyerOnly"], default="public")
    confidentialityRationale = StringType()

    def validate_confidentialityRationale(self, data, val):
        validate_confidentiality_rationale(data, val)

