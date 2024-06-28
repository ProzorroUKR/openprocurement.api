from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.state.award import AwardStateMixing
from openprocurement.tender.openua.constants import STAND_STILL_TIME
from openprocurement.tender.openua.procedure.state.tender import OpenUATenderState


class AwardState(AwardStateMixing, OpenUATenderState):
    award_stand_still_time = STAND_STILL_TIME  # move to tender state class?
    award_stand_still_working_days: bool = False

    def award_status_up_from_active_to_cancelled(self, award, tender):
        if any(i.get("status") == "satisfied" for i in award.get("complaints", "")):
            for i in tender.get("awards", ""):
                if i.get("lotID") == award.get("lotID"):
                    if self.is_available_to_cancel_award(i, [award["id"]]):
                        self.cancel_award(i)
            self.add_next_award()

        else:
            self.cancel_award(award)
            self.add_next_award()

    def award_status_up_from_unsuccessful_to_cancelled(self, award, tender):
        if not self.has_considered_award_complaints(award, tender):
            raise_operation_error(self.request, "Can't update award in current (unsuccessful) status")

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

    @staticmethod
    def has_considered_award_complaints(current_award, tender):
        considered_statuses = ("satisfied", "resolved")
        for award in tender.get("awards", []):
            if tender.get("lots") and award["lotID"] != current_award["lotID"]:
                continue
            for complaint in award.get("complaints", ""):
                if complaint["status"] in considered_statuses:
                    return True
        return False
