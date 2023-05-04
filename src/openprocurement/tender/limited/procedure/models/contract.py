from openprocurement.tender.core.procedure.models.contract import (
    PatchContract as BasePatchContract,
    Contract as BaseContract,
)
from openprocurement.tender.core.procedure.models.organization import ContactLessBusinessOrganization
from openprocurement.api.context import get_now
from schematics.exceptions import ValidationError
from openprocurement.tender.core.procedure.models.base import (
    ModelType, ListType,
)


class ReportingContract(BaseContract):
    suppliers = ListType(ModelType(ContactLessBusinessOrganization, required=True),
                         min_size=1, max_size=1)

    def validate_dateSigned(self, data, value):
        if value and value > get_now():
            raise ValidationError("Contract signature date can't be in the future")
    

class ReportingPostContract(ReportingContract):
    pass


class ReportingPatchContract(BasePatchContract):
    suppliers = ListType(ModelType(ContactLessBusinessOrganization, required=True),
                         min_size=1, max_size=1)


class NegotiationContract(BaseContract):
    pass


class NegotiationPostContract(NegotiationContract):
    pass


class NegotiationPatchContract(BasePatchContract):
    pass

