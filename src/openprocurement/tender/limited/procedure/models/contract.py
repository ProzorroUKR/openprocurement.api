from schematics.exceptions import ValidationError

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.types import ListType, ModelType
from openprocurement.tender.core.procedure.models.contract import (
    Contract as BaseContract,
)
from openprocurement.tender.core.procedure.models.contract import (
    PatchContract as BasePatchContract,
)
from openprocurement.tender.core.procedure.models.organization import (
    ContactLessSupplier,
)


class ReportingContract(BaseContract):
    suppliers = ListType(
        ModelType(ContactLessSupplier, required=True),
        min_size=1,
        max_size=1,
    )

    def validate_dateSigned(self, data, value):
        if value and value > get_request_now():
            raise ValidationError("Contract signature date can't be in the future")


class ReportingPostContract(ReportingContract):
    pass


class ReportingPatchContract(BasePatchContract):
    suppliers = ListType(
        ModelType(ContactLessSupplier, required=True),
        min_size=1,
        max_size=1,
    )


class NegotiationContract(BaseContract):
    pass


class NegotiationPostContract(NegotiationContract):
    pass


class NegotiationPatchContract(BasePatchContract):
    pass
