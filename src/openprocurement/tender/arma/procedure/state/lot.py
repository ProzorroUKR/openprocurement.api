from openprocurement.api.constants_env import ARMA_MIN_EXPECTED_INCOME_FROM
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.arma.procedure.state.tender_details import (
    TenderDetailsState,
)
from openprocurement.tender.core.procedure.state.lot import LotInvalidationBidStateMixin
from openprocurement.tender.core.procedure.utils import tender_created_before


class LotState(LotInvalidationBidStateMixin, TenderDetailsState):
    def lot_on_post(self, data: dict) -> None:
        self.validate_lot_min_expected_income(data)
        super().lot_on_post(data)

    def validate_lot_min_expected_income(self, lot: dict) -> None:
        tender = get_tender()

        if tender_created_before(ARMA_MIN_EXPECTED_INCOME_FROM, tender):
            return

        if tender.get("status") == "draft":
            return

        if lot.get("minExpectedIncome") is None:
            raise_operation_error(
                self.request,
                "minExpectedIncome is required for lot",
                status=422,
                name="minExpectedIncome",
            )
