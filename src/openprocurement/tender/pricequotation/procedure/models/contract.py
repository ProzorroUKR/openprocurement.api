from openprocurement.tender.core.procedure.models.contract import (
    Contract as BaseContract,
    PostContract as BasePostContract,
    PatchContract as BasePatchContract,
    PatchContractSupplier as BasePatchContractSupplier,
)
from schematics.exceptions import ValidationError
from openprocurement.api.utils import get_now
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.core.procedure.utils import dt_from_iso


class Contract(BaseContract):
    def validate_dateSigned(self, data, value):
        parent = get_tender()
        if value:
            if value > get_now():
                raise ValidationError("Contract signature date can't be in the future")
            active_award = [award for award in parent.get("awards", []) if award.get("status") == "active"]
            if active_award and value < dt_from_iso(active_award[0].get("date")):
                raise ValidationError(
                    f"Contract signature date should be "
                    f"after award activation date ({active_award[0]['date']})"
                )


class PostContract(BasePostContract):
    pass


class PatchContract(BasePatchContract):
    pass


class PatchContractSupplier(BasePatchContractSupplier):
    pass
