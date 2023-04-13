from decimal import Decimal

from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.esco.procedure.state.tender import ESCOTenderTenderState
from openprocurement.tender.esco.procedure.state.tender_details import TenderDetailsState
from openprocurement.tender.core.procedure.state.lot import LotInvalidationBidStateMixin
from openprocurement.api.utils import raise_operation_error


class TenderLotState(LotInvalidationBidStateMixin, ESCOTenderTenderState):

    tender_details_state_class = TenderDetailsState

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
        if tender["fundingKind"] == "budget" and (value > Decimal("0.8") or value < Decimal("0")):
            raise_operation_error(
                self.request,
                "when tender fundingKind is budget, yearlyPaymentsPercentageRange "
                "should be less or equal 0.8, and more or equal 0",
                status=422,
                name="yearlyPaymentsPercentageRange",
            )