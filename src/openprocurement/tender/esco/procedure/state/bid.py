from decimal import Decimal

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.utils import to_decimal
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.state.bid import BidState
from openprocurement.tender.esco.procedure.models.bid import (
    PatchBid,
    PatchQualificationBid,
)


class ESCOBidState(BidState):
    def on_post(self, data):
        super().on_post(data)
        self.set_yearly_payments_percentage_for_lots(data)

    def on_patch(self, before, after):
        super().on_patch(before, after)
        self.set_yearly_payments_percentage_for_lots(after)

    def set_yearly_payments_percentage_for_lots(self, bid):
        tender = get_tender()
        if tender["fundingKind"] == "budget" and tender.get("lots"):
            for lv in bid.get("lotValues", []):
                yearly_value = to_decimal(lv["value"]["yearlyPaymentsPercentage"])
                lots = [i for i in tender.get("lots", "") if i["id"] == lv["relatedLot"]]

                max_value = lots[0]["yearlyPaymentsPercentageRange"]
                if lots and yearly_value > Decimal(str(max_value)):
                    raise_operation_error(
                        self.request,
                        f"yearlyPaymentsPercentage should be greater than 0 and less than {max_value}",
                        status=422,
                        name="lotValues.value",
                    )

    def get_patch_data_model(self):
        tender = self.request.validated["tender"]
        if tender.get("status", "") in self.qualification_statuses:
            return PatchQualificationBid
        return PatchBid
