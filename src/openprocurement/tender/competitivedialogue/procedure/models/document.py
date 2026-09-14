from schematics.types import BooleanType

from openprocurement.tender.core.procedure.models.document import Document, PatchDocument, PostDocument


class CDBidPostDocument(PostDocument):
    isDescriptionDecision = BooleanType(default=False)

    def validate_confidentialityRationale(self, data, val):
        if not data.get("isDescriptionDecision"):
            return super().validate_confidentialityRationale(self, data, val)


class CDBidPatchDocument(PatchDocument):
    isDescriptionDecision = BooleanType()

    def validate_confidentialityRationale(self, data, val):
        pass


class CDBidDocument(Document):
    isDescriptionDecision = BooleanType()

    def validate_confidentialityRationale(self, data, val):
        if not data.get("isDescriptionDecision"):
            return super().validate_confidentialityRationale(self, data, val)
