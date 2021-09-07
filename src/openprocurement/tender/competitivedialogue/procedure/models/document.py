from openprocurement.tender.openeu.procedure.models.document import (
    PostDocument as BasePostDocument,
    PatchDocument as BasePatchDocument,
    Document as BaseDocument,
)
from schematics.types import BooleanType


class PostDocument(BasePostDocument):
    isDescriptionDecision = BooleanType(default=False)

    def validate_confidentialityRationale(self, data, val):
        if not data.get("isDescriptionDecision"):
            return super().validate_confidentialityRationale(self, data, val)


class PatchDocument(BasePatchDocument):
    isDescriptionDecision = BooleanType()

    def validate_confidentialityRationale(self, data, val):
        pass


class Document(BaseDocument):
    isDescriptionDecision = BooleanType()

    def validate_confidentialityRationale(self, data, val):
        if not data.get("isDescriptionDecision"):
            return super().validate_confidentialityRationale(self, data, val)
