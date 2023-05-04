from openprocurement.tender.core.procedure.state.award import AwardStateMixing
from openprocurement.tender.core.procedure.context import get_request, get_tender
from openprocurement.api.context import get_now
from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState
from openprocurement.api.utils import raise_operation_error


class AwardState(AwardStateMixing, CFAUATenderState):

    def award_on_patch(self, before, award):
        # start complaintPeriod
        if before["status"] != award["status"]:
            if award["status"] == "unsuccessful":
                award["complaintPeriod"] = {"startDate": get_now().isoformat()}

            self.award_status_up(before["status"], award["status"], award)
        elif award["status"] == "pending":
            pass  # allowing to update award in pending status
        else:
            raise_operation_error(get_request(),
                                  f"Can't update award in current ({before['status']}) status")

    def award_status_up(self, before, after, award):
        assert before != after, "Statuses must be different"
        tender = get_tender()
        now = get_now().isoformat()

        # TODO: split into functions like award_status_from_pending_to_active ?
        if before == "pending" and after == "active":
            pass

        elif before == "pending" and after == "unsuccessful":
            award["complaintPeriod"]["endDate"] = now
            self.add_next_award()

        elif before == "active" and after == "cancelled":
            if tender["status"] == "active.qualification.stand-still":
                for aw in tender.get("awards"):
                    if aw.get("lotID") == award.get("lotID"):
                        self.set_object_status(aw, "cancelled")

                self.add_next_award(
                    regenerate_all_awards=True,
                    lot_id=award["lotID"],
                )

                # award["dateDecision"] = now  # wtf ?
                period = tender.get("awardPeriod")
                if period and "endDate" in period:
                    del period["endDate"]

                ensure_status = "active.qualification"
                if tender["status"] != ensure_status:
                    handler = self.get_change_tender_status_handler(ensure_status)
                    handler(tender)
            else:
                self.add_next_award(lot_id=award["lotID"])

        elif before == "unsuccessful" and after == "cancelled":
            for aw in tender.get("awards", ""):
                if aw.get("lotID") == award.get("lotID"):
                    self.set_object_status(aw, "cancelled")
            self.add_next_award(
                regenerate_all_awards=True,
                lot_id=award["lotID"],
            )

        else:  # any other state transitions are forbidden
            raise_operation_error(get_request(),
                                  f"Can't update award in current ({before}) status")
        # date updated when status updated
        award["date"] = get_now().isoformat()

