from openprocurement.api.context import get_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.state.award import AwardStateMixing
from openprocurement.tender.open.procedure.state.tender import OpenTenderState


class AwardState(AwardStateMixing, OpenTenderState):

    def award_status_up(self, before, after, award):
        assert before != after, "Statuses must be different"
        tender = get_tender()
        awarding_order_enabled = tender["config"]["hasAwardingOrder"]
        now = get_now().isoformat()
        award_complaint = tender["config"]["awardComplainDuration"]

        if before == "pending" and after == "active":
            self.award_status_up_from_pending_to_active(award, tender, awarding_order_enabled)

        elif before == "pending" and after == "unsuccessful":
            self.award_status_up_from_pending_to_unsuccessful(award, tender)

        elif before == "active" and after == "cancelled":
            if any(i.get("status") == "satisfied" for i in award.get("complaints", "")):
                for i in tender.get("awards", ""):
                    if i.get("lotID") == award.get("lotID"):
                        if award_complaint > 0:
                            period = i.get("complaintPeriod")
                            if period:
                                if not period.get("endDate") or period["endDate"] > now:
                                    period["endDate"] = now
                        if self.is_available_to_cancel_award(i, [award["id"]]):
                            self.cancel_award(i)
                self.add_next_award()

            else:
                if award_complaint > 0 and award["complaintPeriod"]["endDate"] > now:
                    award["complaintPeriod"]["endDate"] = now
                self.cancel_award(award)
                self.add_next_award()

        elif before == "unsuccessful" and after == "cancelled" and self.has_considered_award_complaints(award, tender):
            self.award_status_up_from_unsuccessful_to_cancelled(award, tender)

        else:  # any other state transitions are forbidden
            raise_operation_error(get_request(), f"Can't update award in current ({before}) status")
        # date updated when status updated
        award["date"] = get_now().isoformat()

    def award_status_up_from_unsuccessful_to_cancelled(self, award, tender, awarding_order_enabled=False):
        award_complaint = tender["config"]["awardComplainDuration"]
        now = get_now().isoformat()
        if tender["status"] == "active.awarded":
            self.set_object_status(tender, "active.qualification")
            if "endDate" in tender["awardPeriod"]:
                del tender["awardPeriod"]["endDate"]
        if award_complaint > 0:
            if award["complaintPeriod"]["endDate"] > now:
                award["complaintPeriod"]["endDate"] = now

        for i in tender.get("awards", ""):
            if i.get("lotID") == award.get("lotID"):
                if award_complaint > 0:
                    period = i.get("complaintPeriod")
                    if period:
                        if not period.get("endDate") or period["endDate"] > now:
                            period["endDate"] = now

                if self.is_available_to_cancel_award(i, [award["id"]]):
                    self.cancel_award(i)
        self.add_next_award()
