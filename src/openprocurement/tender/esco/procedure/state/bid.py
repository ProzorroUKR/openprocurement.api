from decimal import Decimal

from schematics.exceptions import ValidationError

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.utils import to_decimal
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.state.bid import BidState
from openprocurement.tender.core.procedure.validation import validate_esco_lotvalue_value
from openprocurement.tender.esco.procedure.models.bid import (
    ESCOBid,
    ESCOPatchBid,
    ESCOPatchQualificationBid,
    ESCOPostBid,
)


class ESCOBidState(BidState):
    bid_post_data_model = ESCOPostBid
    bid_patch_data_model = ESCOPatchBid
    bid_patch_qualification_data_model = ESCOPatchQualificationBid
    bid_data_model = ESCOBid

    self_eligible_required = False
    bid_items_quantity_required = False

    def on_post(self, data):
        super().on_post(data)
        self.set_yearly_payments_percentage_for_lots(data)

    def on_patch(self, before, after):
        super().on_patch(before, after)
        self.set_yearly_payments_percentage_for_lots(after)

    def validate_bid_lot_value_against_lot(self, tender, lot_value):
        if lot_value.get("status") != "draft" and lot_value["value"] is not None:
            validate_esco_lotvalue_value(tender, lot_value.get("relatedLot"), lot_value["value"])

    def get_bid_value_errors(self, tender, value) -> dict:
        """former ESCODynamicValue.validate_yearlyPaymentsPercentage (lots: the lot range is checked on post / patch)"""
        if not value or value.get("yearlyPaymentsPercentage") is None:
            return {}
        yearly = to_decimal(value["yearlyPaymentsPercentage"])
        if tender["fundingKind"] == "other" and yearly < Decimal("0.8"):
            return {"yearlyPaymentsPercentage": ["yearlyPaymentsPercentage should be greater than 0.8 and less than 1"]}
        if not tender.get("lots") and tender["fundingKind"] == "budget":
            max_value = tender["yearlyPaymentsPercentageRange"]
            if yearly > Decimal(str(max_value)):
                return {
                    "yearlyPaymentsPercentage": [
                        f"yearlyPaymentsPercentage should be greater than 0 and less than {max_value}"
                    ]
                }
        return {}

    def validate_bid_value_against_tender(self, tender, value):
        """former ESCOBidMixin.validate_value: the bid value is checked against the tender minValue"""
        if tender.get("lots"):
            if value:
                raise ValidationError("value should be posted for each lot of bid")
        else:
            if not value:
                raise ValidationError("This field is required.")
            if tender["minValue"].get("currency") != value.get("currency"):
                raise ValidationError("currency of bid should be identical to currency of minValue of tender")
            if tender["minValue"].get("valueAddedTaxIncluded") != value.get("valueAddedTaxIncluded"):
                raise ValidationError(
                    "valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of minValue of tender"
                )

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
