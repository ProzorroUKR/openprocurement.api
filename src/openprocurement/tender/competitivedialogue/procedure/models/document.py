from openprocurement.api.models import Model
from openprocurement.tender.openua.procedure.models.document import (
    PostDocument as BasePostDocument,
    PatchDocument as BasePatchDocument,
    Document as BaseDocument,
)
from schematics.types import BooleanType
from schematics.exceptions import ValidationError


class Stage1Mixin(Model):
    isDescriptionDecision = BooleanType(default=False)

    def validate_confidentialityRationale(self, data, val):
        if data["confidentiality"] != "public" and not data["isDescriptionDecision"]:
            if not val:
                raise ValidationError("confidentialityRationale is required")
            elif len(val) < 30:
                raise ValidationError("confidentialityRationale should contain at least 30 characters")


class PostDocument(Stage1Mixin, BasePostDocument):
    pass


class PatchDocument(BasePatchDocument):
    isDescriptionDecision = BooleanType()

    def validate_confidentialityRationale(self, data, val):
        pass


class Document(Stage1Mixin, BaseDocument):
    pass
