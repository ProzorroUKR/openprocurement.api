from openprocurement.api.models import Model
from openprocurement.tender.core.procedure.models.document import (
    PostDocument as BasePostDocument,
    PatchDocument as BasePatchDocument,
    Document as BaseDocument,
)
from schematics.types import StringType
from schematics.exceptions import ValidationError


class ConfidentialityMixin(Model):
    confidentiality = StringType(choices=["public", "buyerOnly"], default="public")
    confidentialityRationale = StringType()

    def validate_confidentialityRationale(self, data, val):
        confidentiality = data.get("confidentiality")
        if confidentiality == "buyerOnly":
            if not val:
                raise ValidationError("confidentialityRationale is required")
            elif len(val) < 30:
                raise ValidationError("confidentialityRationale should contain at least 30 characters")


class PostDocument(BasePostDocument, ConfidentialityMixin):
    language = StringType(choices=["uk", "en", "ru"])


class PatchDocument(BasePatchDocument, ConfidentialityMixin):
    confidentiality = StringType(choices=["public", "buyerOnly"])
    language = StringType(choices=["uk", "en", "ru"])


class Document(BaseDocument, ConfidentialityMixin):
    language = StringType(choices=["uk", "en", "ru"])
