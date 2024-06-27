from openprocurement.api.context import get_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.state.award import AwardStateMixing
from openprocurement.tender.openua.constants import STAND_STILL_TIME
from openprocurement.tender.openua.procedure.state.tender import OpenUATenderState


class AwardState(AwardStateMixing, OpenUATenderState):
    award_stand_still_time = STAND_STILL_TIME  # move to tender state class?

    def award_status_up(self, before, after, award):
        assert before != after, "Statuses must be different"
        tender = get_tender()
        awarding_order_enabled = tender["config"]["hasAwardingOrder"]
        now = get_now().isoformat()

        if before == "pending" and after == "active":
            self.award_status_up_from_pending_to_active(award, tender, awarding_order_enabled)

        elif before == "pending" and after == "unsuccessful":
            self.award_status_up_from_pending_to_unsuccessful(award, tender)

        elif before == "active" and after == "cancelled":
            if any(i.get("status") == "satisfied" for i in award.get("complaints", "")):
                for i in tender.get("awards", ""):
                    if i.get("lotID") == award.get("lotID"):
                        if self.is_available_to_cancel_award(i, [award["id"]]):
                            self.cancel_award(i)
                self.add_next_award()

            else:
                self.cancel_award(award)
                self.add_next_award()

        elif before == "unsuccessful" and after == "cancelled" and self.has_considered_award_complaints(award, tender):
            self.award_status_up_from_unsuccessful_to_cancelled(award, tender, awarding_order_enabled)

        else:  # any other state transitions are forbidden
            raise_operation_error(get_request(), f"Can't update award in current ({before}) status")
        # date updated when status updated
        award["date"] = get_now().isoformat()

    def award_status_up_from_unsuccessful_to_cancelled(self, award, tender, awarding_order_enabled=False):
        if tender["status"] == "active.awarded":
            # Go back to active.qualification status
            # because there is no active award anymore
            # for at least one of the lots
            tender["awardPeriod"].pop("endDate", None)
            self.get_change_tender_status_handler("active.qualification")(tender)

        for i in tender.get("awards"):
            if i.get("lotID") == award.get("lotID"):
                if self.is_available_to_cancel_award(i, [award["id"]]):
                    self.cancel_award(i)

        self.cancel_award(award)
        self.add_next_award()
