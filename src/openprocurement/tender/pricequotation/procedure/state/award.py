from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.contracting import add_contracts
from openprocurement.tender.core.procedure.state.award import AwardStateMixing
from openprocurement.tender.pricequotation.procedure.state.tender import (
    PriceQuotationTenderState,
)


class AwardState(AwardStateMixing, PriceQuotationTenderState):
    procurement_kinds_not_required_sign = ("other",)  # in case when signing award will be required in the future
    award_unsuccessful_cancel_allowed = False

    def award_status_up_from_pending_to_active(self, award, tender):
        self.request.validated["contracts_added"] = add_contracts(self.request, award)
        self.add_next_award()

    def award_status_up_from_active_to_cancelled(self, award, tender):
        self.cancel_award(award)
        self.add_next_award()

    def award_status_up_from_pending_to_unsuccessful(self, award, tender):
        self.add_next_award()

    def award_status_up_from_unsuccessful_to_cancelled(self, award, tender):
        if self.has_active_contract(award, tender):
            raise_operation_error(self.request, "Can't update award in current (unsuccessful) status")

        if tender["status"] == "active.awarded":
            # Go back to active.qualification status
            # because there is no active award anymore
            # for at least one of the lots
            tender["awardPeriod"].pop("endDate", None)
            self.get_change_tender_status_handler("active.qualification")(tender)

        for i in tender.get("awards", ""):
            if i.get("lotID") == award.get("lotID"):
                if self.is_available_to_cancel_award(i, [award["id"]]):
                    self.cancel_award(i)

        self.cancel_award(award)
        self.add_next_award()
