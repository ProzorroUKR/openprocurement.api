from openprocurement.api.constants_env import (
    NEW_DEFENSE_COMPLAINTS_FROM,
    NEW_DEFENSE_COMPLAINTS_TO,
)
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.contracting import add_contracts
from openprocurement.tender.core.procedure.state.award import AwardStateMixing
from openprocurement.tender.core.procedure.utils import tender_created_in
from openprocurement.tender.openuadefense.procedure.state.tender import (
    OpenUADefenseTenderState,
)


class AwardState(AwardStateMixing, OpenUADefenseTenderState):
    award_stand_still_working_days: bool = True

    def award_status_up_from_pending_to_active(self, award, tender):
        self.set_award_complaint_period(award)
        new_defence_complaints = tender_created_in(NEW_DEFENSE_COMPLAINTS_FROM, NEW_DEFENSE_COMPLAINTS_TO)
        if new_defence_complaints and award.get("complaintPeriod"):
            for i in tender.get("awards"):
                if i.get("lotID") == award.get("lotID") and i.get("status") == "unsuccessful":
                    i["complaintPeriod"] = award["complaintPeriod"]
        self.request.validated["contracts_added"] = add_contracts(self.request, award)
        self.add_next_award()

    def award_status_up_from_active_to_cancelled(self, award, tender):
        new_defence_complaints = tender_created_in(NEW_DEFENSE_COMPLAINTS_FROM, NEW_DEFENSE_COMPLAINTS_TO)
        if any(i.get("status") == "satisfied" for i in award.get("complaints", "")):
            for i in tender.get("awards", ""):
                if i.get("lotID") == award.get("lotID"):
                    if self.is_available_to_cancel_award(i, [award["id"]]):
                        self.cancel_award(i, end_complaint_period=not new_defence_complaints)

            self.add_next_award()
        else:
            self.cancel_award(award, end_complaint_period=not new_defence_complaints)
            self.add_next_award()

    def award_status_up_from_pending_to_unsuccessful(self, award, tender):
        new_defence_complaints = tender_created_in(NEW_DEFENSE_COMPLAINTS_FROM, NEW_DEFENSE_COMPLAINTS_TO)
        if not new_defence_complaints:
            self.set_award_complaint_period(award)
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

        new_defence_complaints = tender_created_in(NEW_DEFENSE_COMPLAINTS_FROM, NEW_DEFENSE_COMPLAINTS_TO)

        for i in tender.get("awards"):
            if i.get("lotID") == award.get("lotID"):
                if self.is_available_to_cancel_award(i, [award["id"]]):
                    self.cancel_award(i, end_complaint_period=not new_defence_complaints)

        self.cancel_award(award, end_complaint_period=not new_defence_complaints)
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
