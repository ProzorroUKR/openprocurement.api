from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.state.award import AwardStateMixing
from openprocurement.tender.requestforproposal.procedure.state.tender import (
    RequestForProposalTenderState,
)


class AwardState(AwardStateMixing, RequestForProposalTenderState):
    sign_award_required = False

    def award_status_up_from_unsuccessful_to_cancelled(self, award, tender):
        if self.has_active_contract(award, tender):
            raise_operation_error(self.request, "Can't update award in current (unsuccessful) status")

        if tender["status"] == "active.awarded":
            # Go back to active.qualification status
            # because there is no active award anymore
            # for at least one of the lots
            tender["awardPeriod"].pop("endDate", None)
            self.get_change_tender_status_handler("active.qualification")(tender)

        if tender["config"]["hasAwardingOrder"]:
            # If hasAwardingOrder is True, then the current award should be found through all
            # tender awards/lot awards. Then the current award and next ones after it should be cancelled.
            # The new 'pending' award will be generated instead of current one.
            # And qualification will be continued starting from this new award.
            skip = True
            for i in tender.get("awards"):
                # skip all award before the context one
                if i["id"] == award["id"]:
                    skip = False
                if skip:
                    continue
                # skip different lot awards
                if i.get("lotID") != award.get("lotID"):
                    continue
                self.set_award_complaints_cancelled(i)
                self.cancel_award(i)

        self.set_award_complaints_cancelled(award)
        self.cancel_award(award)
        self.add_next_award()
