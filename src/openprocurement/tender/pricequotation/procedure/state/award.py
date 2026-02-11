from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.contracting import add_contracts
from openprocurement.tender.core.procedure.state.award import AwardStateMixing
from openprocurement.tender.pricequotation.procedure.state.tender import (
    PriceQuotationTenderState,
)


class AwardState(AwardStateMixing, PriceQuotationTenderState):
    procurement_kinds_not_required_sign = ("other",)  # in case when signing award will be required in the future

    def award_status_up_from_pending_to_active(self, award, tender):
        self.request.validated["contracts_added"] = add_contracts(self.request, award)
        self.add_next_award()

    def award_status_up_from_active_to_cancelled(self, award, tender):
        self.cancel_award(award)
        self.add_next_award()

    def award_status_up_from_pending_to_unsuccessful(self, award, tender):
        self.add_next_award()

    def award_status_up_from_unsuccessful_to_cancelled(self, award, tender):
        raise_operation_error(self.request, "Can't update award in current (unsuccessful) status")
