from decimal import Decimal

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.state.lot import LotStateMixin
from openprocurement.tender.esco.procedure.models.lot import ESCOLot, ESCOPatchLot, ESCOPostLot
from openprocurement.tender.esco.procedure.state.tender_details import (
    ESCOTenderDetailsState,
)


class TenderLotState(LotStateMixin, ESCOTenderDetailsState):
    post_data_model = ESCOPostLot
    patch_data_model = ESCOPatchLot
    data_model = ESCOLot

    invalidate_bids_on_lot_change = True

    def pre_save_validations(self, data: dict) -> None:
        super().pre_save_validations(data)
        self.validate_yearly_payments_percentage_range(data)

    def validate_yearly_payments_percentage_range(self, data: dict) -> None:
        tender = get_tender()
        value = data.get("yearlyPaymentsPercentageRange")
        if tender["fundingKind"] == "other" and value != Decimal("0.8"):
            raise_operation_error(
                self.request,
                "when tender fundingKind is other, yearlyPaymentsPercentageRange should be equal 0.8",
                status=422,
                name="yearlyPaymentsPercentageRange",
            )
        if tender["fundingKind"] == "budget" and (value is None or value > Decimal("0.8") or value < Decimal("0")):
            raise_operation_error(
                self.request,
                "when tender fundingKind is budget, yearlyPaymentsPercentageRange "
                "should be less or equal 0.8, and more or equal 0",
                status=422,
                name="yearlyPaymentsPercentageRange",
            )

    def set_lot_data(self, data: dict) -> None:
        tender = get_tender()
        self.set_auction_period_should_start_after(tender, data)
        self.set_tender_lot_data(tender, data)
