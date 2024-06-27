from openprocurement.api.context import get_now
from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState
from openprocurement.tender.core.procedure.state.award import AwardStateMixing


class AwardState(AwardStateMixing, CFAUATenderState):

    def award_status_up_from_pending_to_active(self, award, tender):
        pass

    def award_status_up_from_active_to_cancelled(self, award, tender):
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

    def award_status_up_from_pending_to_unsuccessful(self, award, tender):
        award["complaintPeriod"] = {
            "startDate": get_now().isoformat(),
            "endDate": get_now().isoformat(),
        }
        self.add_next_award()

    def award_status_up_from_unsuccessful_to_cancelled(self, award, tender):
        for i in tender.get("awards", ""):
            if i.get("lotID") == award.get("lotID"):
                self.set_object_status(i, "cancelled")
        self.add_next_award(
            regenerate_all_awards=True,
            lot_id=award["lotID"],
        )
