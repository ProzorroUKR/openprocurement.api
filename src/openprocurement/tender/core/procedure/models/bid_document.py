from schematics.types import StringType

from openprocurement.api.procedure.models.document import (
    ConfidentialityTypes,
    validate_confidentiality_rationale,
)
from openprocurement.tender.core.procedure.models.document import (
    Document as BaseDocument,
)
from openprocurement.tender.core.procedure.models.document import (
    PatchDocument as BasePatchDocument,
)
from openprocurement.tender.core.procedure.models.document import (
    PostDocument as BasePostDocument,
)


class PostDocument(BasePostDocument):
    confidentiality = StringType(
        choices=[ConfidentialityTypes.PUBLIC.value, ConfidentialityTypes.BUYER_ONLY.value],
        default=ConfidentialityTypes.PUBLIC.value,
    )
    confidentialityRationale = StringType()

    def validate_confidentialityRationale(self, data, val):
        validate_confidentiality_rationale(data, val)


class PatchDocument(BasePatchDocument):
    confidentiality = StringType(choices=[ConfidentialityTypes.PUBLIC.value, ConfidentialityTypes.BUYER_ONLY.value])
    confidentialityRationale = StringType()


class Document(BaseDocument):
    confidentiality = StringType(
        choices=[ConfidentialityTypes.PUBLIC.value, ConfidentialityTypes.BUYER_ONLY.value],
        default=ConfidentialityTypes.PUBLIC.value,
    )
    confidentialityRationale = StringType()

    def validate_confidentialityRationale(self, data, val):
        validate_confidentiality_rationale(data, val)
