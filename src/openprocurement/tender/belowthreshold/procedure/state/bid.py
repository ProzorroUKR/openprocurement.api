from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.state.bid import BidState


class BelowThresholdBidState(BidState):
    def on_post(self, data):
        self.validate_bid_unit_value(data)
        super().on_post(data)

    def on_patch(self, before, after):
        self.validate_bid_unit_value(after)
        super().on_patch(before, after)

    def validate_bid_unit_value(self, data):
        tender = get_tender()
        for item in data.get("items", []):
            if value := item.get("unit", {}).get("value"):
                if tender["value"]["valueAddedTaxIncluded"] != value.get("valueAddedTaxIncluded"):
                    raise_operation_error(
                        self.request,
                        "valueAddedTaxIncluded of bid unit should be identical to valueAddedTaxIncluded of tender value",
                        name="items",
                        status=422,
                    )
            elif tender.get("funders"):
                raise_operation_error(
                    self.request,
                    "items.unit.value is required for tender with funders",
                    name="items",
                    status=422,
                )
