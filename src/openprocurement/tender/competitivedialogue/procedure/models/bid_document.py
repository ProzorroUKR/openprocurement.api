from schematics.types import BooleanType

from openprocurement.tender.core.procedure.models.bid_document import (
    Document as BaseDocument,
)
from openprocurement.tender.core.procedure.models.bid_document import (
    PatchDocument as BasePatchDocument,
)
from openprocurement.tender.core.procedure.models.bid_document import (
    PostDocument as BasePostDocument,
)


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
