from decimal import Decimal

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.utils import to_decimal
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.state.bid import BidState


class ESCOBidState(BidState):
    self_eligible_required = False
    bid_items_quantity_required = False
    bid_value_validation_on_patch = False  # value is validated by the procedure's own bid model

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
