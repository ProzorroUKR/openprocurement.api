from decimal import Decimal

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.utils import to_decimal
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.state.bid import BidState


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

                if lots and yearly_value > Decimal(lots[0]["yearlyPaymentsPercentageRange"]):
                    raise_operation_error(
                        self.request,
                        f"yearlyPaymentsPercentage should be greater than 0 and less than {lots[0]['yearlyPaymentsPercentageRange']}",
                        status=422,
                        name="lotValues.value",
                    )
