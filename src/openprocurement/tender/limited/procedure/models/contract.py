from openprocurement.tender.core.procedure.models.contract import (
    PatchContractSupplier as BasePatchContractSupplier,
    PatchContract as BasePatchContract,
    Contract as BaseContract,
)
from openprocurement.tender.core.procedure.context import get_now
from schematics.exceptions import ValidationError


class ReportingContract(BaseContract):
    def validate_dateSigned(self, data, value):
        if value and value > get_now():
            raise ValidationError("Contract signature date can't be in the future")
    

class ReportingPostContract(ReportingContract):
    pass


class ReportingPatchContract(BasePatchContract):
    pass


class NegotiationContract(BaseContract):
    pass


class NegotiationPostContract(NegotiationContract):
    pass


class NegotiationPatchContract(BasePatchContract):
    pass

